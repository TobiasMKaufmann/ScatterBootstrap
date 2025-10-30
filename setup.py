import os
import sys
import subprocess
import glob
import shutil
from setuptools import setup, find_packages
from setuptools.command.build_py import build_py

class BuildSharedLibraries(build_py):
    """Custom build command to compile C files as shared libraries"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.msvc_env = None
    
    def setup_msvc_environment(self):
        """Set up MSVC environment variables for compilation on Windows"""
        if sys.platform != 'win32':
            return True
        
        # Check if cl.exe is already in PATH
        try:
            subprocess.run(['cl'], capture_output=True, text=True, check=False)
            print("  [OK] MSVC compiler found in PATH")
            # Use the current environment as-is
            self.msvc_env = os.environ.copy()
            return True
        except FileNotFoundError:
            pass
        
        # Try to find Build Tools installation
        buildtools_paths = [
            r'C:\BuildTools',
            r'C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools',
            r'C:\Program Files (x86)\Microsoft Visual Studio\2019\BuildTools',
        ]
        
        msvc_path = None
        for base_path in buildtools_paths:
            if os.path.exists(base_path):
                # Find the MSVC version directory
                vc_tools = os.path.join(base_path, 'VC', 'Tools', 'MSVC')
                if os.path.exists(vc_tools):
                    versions = sorted(os.listdir(vc_tools), reverse=True)
                    if versions:
                        msvc_path = os.path.join(vc_tools, versions[0])
                        break
        
        if not msvc_path:
            print("\n" + "="*70)
            print("ERROR: Microsoft C/C++ Compiler not found!")
            print("="*70)
            print("\nSearched in:")
            for path in buildtools_paths:
                print(f"  - {path}")
            print("\nPlease ensure Microsoft C++ Build Tools are installed.")
            print("="*70 + "\n")
            sys.exit(1)
        
        # Set up environment variables
        print(f"  [OK] Found MSVC at: {msvc_path}")
        
        bin_path = os.path.join(msvc_path, 'bin', 'Hostx64', 'x64')
        lib_path = os.path.join(msvc_path, 'lib', 'x64')
        include_path = os.path.join(msvc_path, 'include')
        
        # Find Windows SDK
        sdk_paths = [
            r'C:\Program Files (x86)\Windows Kits\10',
            r'C:\BuildTools\Windows Kits\10',
        ]
        
        sdk_include = None
        sdk_lib = None
        for sdk_base in sdk_paths:
            if os.path.exists(sdk_base):
                sdk_include_base = os.path.join(sdk_base, 'Include')
                if os.path.exists(sdk_include_base):
                    versions = sorted(os.listdir(sdk_include_base), reverse=True)
                    for version in versions:
                        ucrt_include = os.path.join(sdk_include_base, version, 'ucrt')
                        um_include = os.path.join(sdk_include_base, version, 'um')
                        if os.path.exists(ucrt_include):
                            sdk_include = sdk_include_base
                            sdk_lib = os.path.join(sdk_base, 'Lib', version)
                            print(f"  [OK] Found Windows SDK: {version}")
                            break
                if sdk_include:
                    break
        
        # Create environment with updated PATH and variables
        env = os.environ.copy()
        
        # Update PATH
        new_paths = [bin_path]
        if 'PATH' in env:
            new_paths.append(env['PATH'])
        env['PATH'] = ';'.join(new_paths)
        
        # Set INCLUDE paths
        include_paths = [include_path]
        if sdk_include:
            latest_version = sorted(os.listdir(sdk_include), reverse=True)[0]
            include_paths.extend([
                os.path.join(sdk_include, latest_version, 'ucrt'),
                os.path.join(sdk_include, latest_version, 'um'),
                os.path.join(sdk_include, latest_version, 'shared'),
            ])
        env['INCLUDE'] = ';'.join(include_paths)
        
        # Set LIB paths
        lib_paths = [lib_path]
        if sdk_lib:
            lib_paths.extend([
                os.path.join(sdk_lib, 'ucrt', 'x64'),
                os.path.join(sdk_lib, 'um', 'x64'),
            ])
        env['LIB'] = ';'.join(lib_paths)
        
        self.msvc_env = env
        print("  [OK] MSVC environment configured")
        return True
    
    def run(self):
        # Set up MSVC environment if on Windows
        if sys.platform == 'win32':
            self.setup_msvc_environment()
        
        # First, build the global SAS library
        self.build_sas_core_lib()
        
        # Build all form factor models
        form_factors = [
            'sphere', 'ellipsoid', 'barbell', 'core_shell_cylinder',
            'core_multi_shell', 'elliptical_cylinder', 'fuzzy_sphere',
            'lamellar_hg', 'linear_pearls', 'onion', 'polymer_micelle',
            'pringle', 'bcc_paracrystal', 'fcc_paracrystal'
        ]
        
        for model in form_factors:
            self.build_form_factor(model)
        
        # Build all structure factor models
        structure_factors = ['hayter_msa', 'hardsphere']
        
        for model in structure_factors:
            self.build_structure_factor(model)
        
        # Continue with the normal build
        build_py.run(self)
    
    def build_sas_core_lib(self):
        """Build the global SAS core library"""
        print("\n" + "="*70)
        print("Building Global SAS Core Library")
        print("="*70)
        
        lib_sources = [
            'src/lib/sas_J1.c',
            'src/lib/sas_3j1x_x.c',
            'src/lib/sas_J0.c',
            'src/lib/sas_JN.c',
            'src/lib/utils.c',
            'src/lib/gauss76.c',
            'src/lib/gauss150.c',
            'src/lib/polevl.c',
        ]
        
        self.build_shared_lib('libsas_core', lib_sources, 'src/lib')
    
    def build_form_factor(self, model_name):
        """Build a form factor model"""
        model_dir = f'src/form_factor/{model_name}'
        model_file = f'{model_dir}/{model_name}.c'
        
        if os.path.exists(model_file):
            print(f"\nBuilding form factor: {model_name}")
            
            # Check if this is a paracrystal model with sphere_form.c
            sources = [model_file]
            sphere_form_file = f'{model_dir}/sphere_form.c'
            if os.path.exists(sphere_form_file):
                print(f"  Including sphere_form.c")
                sources.append(sphere_form_file)
            
            self.build_shared_lib(
                model_name,
                sources,
                model_dir,
                link_to_sas_core=True
            )
        else:
            print(f"Skipping {model_name}: C file not found")
    
    def build_structure_factor(self, model_name):
        """Build a structure factor model"""
        model_dir = f'src/structure_factor/{model_name}'
        model_file = f'{model_dir}/{model_name}.c'
        
        if os.path.exists(model_file):
            print(f"\nBuilding structure factor: {model_name}")
            self.build_shared_lib(
                model_name,
                [model_file],
                model_dir,
                link_to_sas_core=True
            )
        else:
            print(f"Skipping {model_name}: C file not found")
    
    def detect_exported_functions(self, obj_files):
        """Detect which functions (Fq, Iq) exist in the object files"""
        functions = []
        
        # Find dumpbin.exe
        dumpbin_exe = shutil.which('dumpbin', path=self.msvc_env['PATH'])
        if not dumpbin_exe:
            # Fallback: just try to export both and let linker fail if needed
            return ['Fq']
        
        # Check each object file for symbols
        for obj_file in obj_files:
            try:
                result = subprocess.run(
                    [dumpbin_exe, '/SYMBOLS', obj_file],
                    capture_output=True,
                    text=True,
                    env=self.msvc_env,
                    check=True
                )
                
                # Parse output for function symbols
                # We need to find SECT definitions (not UNDEF) that are External
                for line in result.stdout.splitlines():
                    # Look for external function definitions (not undefined references)
                    # Format: "nnn 00000000 SECT3  notype ()    External     | Fq"
                    # Avoid: "nnn 00000000 UNDEF  notype ()    External     | Iq" (undefined reference)
                    if 'External' in line and 'UNDEF' not in line:
                        # Check for exact matches at end of line
                        line_stripped = line.strip()
                        if line_stripped.endswith('| Fq') or line_stripped.endswith('| _Fq'):
                            if 'Fq' not in functions:
                                functions.append('Fq')
                        if line_stripped.endswith('| Iq') or line_stripped.endswith('| _Iq'):
                            if 'Iq' not in functions:
                                functions.append('Iq')
            except (subprocess.CalledProcessError, FileNotFoundError) as e:
                pass
        
        # If we couldn't detect anything, default to Fq
        if not functions:
            functions = ['Fq']
        
        return functions
    
    def build_shared_lib(self, name, sources, output_dir, link_to_sas_core=False):
        """Build a shared library from C sources"""
        os.makedirs(output_dir, exist_ok=True)
        
        if sys.platform == 'win32':
            # Windows with MSVC
            dll_file = os.path.join(output_dir, f'{name}.dll')
            output_file = os.path.join(output_dir, f'{name}.pyd')
            lib_file = os.path.join(output_dir, f'{name}.lib')
            
            output_dir_win = output_dir.replace('/', '\\')
            lib_dir_win = 'src\\lib'
            
            obj_files = []
            for src in sources:
                base_name = os.path.basename(src).replace('.c', '.obj')
                obj = os.path.join(output_dir, base_name)
                obj_files.append(obj)
            
            try:
                # Compile each source file
                for src, obj in zip(sources, obj_files):
                    src_win = src.replace('/', '\\')
                    obj_win = obj.replace('/', '\\')
                    
                    # Convert to absolute paths
                    src_abs = os.path.abspath(src_win)
                    obj_abs = os.path.abspath(obj_win)
                    output_dir_abs = os.path.abspath(output_dir_win)
                    lib_dir_abs = os.path.abspath(lib_dir_win)
                    
                    # Find cl.exe with the configured environment
                    cl_exe = shutil.which('cl', path=self.msvc_env['PATH'])
                    if not cl_exe:
                        raise FileNotFoundError("cl.exe not found in PATH after environment setup")
                    
                    # Add BUILDING_SAS_CORE define for core library compilation
                    defines = ['/DFLOAT_SIZE=8']
                    if not link_to_sas_core:
                        defines.append('/DBUILDING_SAS_CORE')
                    
                    compile_cmd = [
                        cl_exe, '/c', '/nologo', '/O2', '/MD', '/W3',
                    ]
                    compile_cmd.extend(defines)
                    compile_cmd.extend([
                        f'/I{output_dir_abs}',
                        f'/I{lib_dir_abs}',
                        f'/Tc{src_abs}',
                        f'/Fo{obj_abs}'
                    ])
                    print(f"  Compiling: {os.path.basename(src)}")
                    
                    # Use cwd parameter to avoid UNC path issues with shell=True
                    try:
                        result = subprocess.run(
                            compile_cmd, 
                            check=True, 
                            env=self.msvc_env,
                            capture_output=True,
                            text=True
                        )
                    except subprocess.CalledProcessError as e:
                        print(f"  Compilation failed!")
                        print(f"  Command: {' '.join(compile_cmd)}")
                        print(f"  STDOUT: {e.stdout}")
                        print(f"  STDERR: {e.stderr}")
                        raise
                    except FileNotFoundError as e:
                        print(f"  ERROR: Could not execute compiler!")
                        print(f"  Command: {' '.join(compile_cmd)}")
                        print(f"  Error: {e}")
                        print(f"  PATH: {self.msvc_env.get('PATH', 'NOT SET')[:200]}")
                        raise
                
                # Link
                obj_files_win = [os.path.abspath(obj.replace('/', '\\')) for obj in obj_files]
                dll_file_abs = os.path.abspath(dll_file.replace('/', '\\'))
                lib_file_abs = os.path.abspath(lib_file.replace('/', '\\'))
                
                # Find link.exe with the configured environment
                link_exe = shutil.which('link', path=self.msvc_env['PATH'])
                if not link_exe:
                    raise FileNotFoundError("link.exe not found in PATH after environment setup")
                
                link_cmd = [
                    link_exe, '/DLL', '/nologo',
                    f'/OUT:{dll_file_abs}',
                    f'/IMPLIB:{lib_file_abs}'
                ]
                
                # For core library, export all symbols (double precision only since FLOAT_SIZE=8)
                if not link_to_sas_core:
                    # Functions
                    link_cmd.append('/EXPORT:sas_3j1x_x')
                    link_cmd.append('/EXPORT:sas_2J1x_x')
                    link_cmd.append('/EXPORT:cephes_j1')
                    link_cmd.append('/EXPORT:cephes_j0')
                    link_cmd.append('/EXPORT:cephes_jn')
                    link_cmd.append('/EXPORT:polevl')
                    link_cmd.append('/EXPORT:p1evl')
                    link_cmd.append('/EXPORT:SINCOS')
                    link_cmd.append('/EXPORT:sas_sinx_x')
                    # Gauss quadrature arrays
                    link_cmd.append('/EXPORT:Gauss76Z')
                    link_cmd.append('/EXPORT:Gauss76Wt')
                    link_cmd.append('/EXPORT:Gauss150Z')
                    link_cmd.append('/EXPORT:Gauss150Wt')
                else:
                    # For model libraries, detect and export the available functions
                    exported_functions = self.detect_exported_functions(obj_files_win)
                    for func in exported_functions:
                        link_cmd.append(f'/EXPORT:{func}')
                        print(f"    Exporting: {func}")
                
                link_cmd.extend(obj_files_win)
                
                if link_to_sas_core:
                    sas_core_lib = os.path.abspath('src\\lib\\libsas_core.lib')
                    if os.path.exists(sas_core_lib):
                        link_cmd.append(sas_core_lib)
                    else:
                        print(f"  Warning: libsas_core.lib not found at {sas_core_lib}, linking may fail")
                
                print(f"  Linking: {name}")
                try:
                    result = subprocess.run(
                        link_cmd, 
                        check=True, 
                        env=self.msvc_env,
                        capture_output=True,
                        text=True
                    )
                except subprocess.CalledProcessError as e:
                    print(f"  Linking failed!")
                    print(f"  Command: {' '.join(link_cmd)}")
                    print(f"  STDOUT: {e.stdout}")
                    print(f"  STDERR: {e.stderr}")
                    raise
                
                if os.path.exists(dll_file):
                    if os.path.exists(output_file):
                        os.remove(output_file)
                    os.rename(dll_file, output_file)
                    
                    # For the core library, also keep a copy as .dll for other modules to find as dependency
                    if not link_to_sas_core:
                        dll_copy = dll_file  # This is the original .dll path
                        if not os.path.exists(dll_copy):
                            shutil.copy2(output_file, dll_copy)
                
            finally:
                # Cleanup object files
                for obj in obj_files:
                    if os.path.exists(obj):
                        os.remove(obj)
                
                # Keep .lib file for core library (needed for linking), remove for others
                if link_to_sas_core:
                    lib_file = dll_file.replace('.dll', '.lib')
                    exp_file = dll_file.replace('.dll', '.exp')
                    if os.path.exists(lib_file):
                        os.remove(lib_file)
                    if os.path.exists(exp_file):
                        os.remove(exp_file)
                else:
                    # For core library, only remove .exp file
                    exp_file = dll_file.replace('.dll', '.exp')
                    if os.path.exists(exp_file):
                        os.remove(exp_file)
        else:
            # Linux/Mac with GCC
            output_file = os.path.join(output_dir, f'{name}.so')
            compile_cmd = ['gcc', '-shared', '-fPIC', '-O2', '-DFLOAT_SIZE=8']
            
            # Add include paths
            compile_cmd.extend([f'-I{output_dir}', '-Isrc/lib'])
            
            # Add sources
            compile_cmd.extend(sources)
            
            # Link to sas_core if needed
            if link_to_sas_core:
                # Get absolute path to lib directory
                lib_dir_abs = os.path.abspath('src/lib')
                compile_cmd.extend(['-Lsrc/lib', '-lsas_core'])
                # Add RPATH so the library can find libsas_core.so at runtime
                compile_cmd.append(f'-Wl,-rpath,$ORIGIN/../../lib')
            
            # Output and math library
            compile_cmd.extend(['-o', output_file, '-lm'])
        
            print(f"  Building: {' '.join(compile_cmd)}")
            subprocess.run(compile_cmd, check=True)
        
        print(f"  [OK] Successfully built {output_file}")

# Setup function
setup(
    cmdclass={'build_py': BuildSharedLibraries},
    packages=find_packages('src'),
    package_dir={'': 'src'},
    package_data={
        'lib': ['*.so', '*.pyd', '*.dll'],
        'form_factor.sphere': ['*.so', '*.pyd', '*.dll'],
        'form_factor.ellipsoid': ['*.so', '*.pyd', '*.dll'],
        'form_factor.barbell': ['*.so', '*.pyd', '*.dll'],
        'form_factor.core_shell_cylinder': ['*.so', '*.pyd', '*.dll'],
        'form_factor.core_multi_shell': ['*.so', '*.pyd', '*.dll'],
        'form_factor.elliptical_cylinder': ['*.so', '*.pyd', '*.dll'],
        'form_factor.fuzzy_sphere': ['*.so', '*.pyd', '*.dll'],
        'form_factor.lamellar_hg': ['*.so', '*.pyd', '*.dll'],
        'form_factor.linear_pearls': ['*.so', '*.pyd', '*.dll'],
        'form_factor.onion': ['*.so', '*.pyd', '*.dll'],
        'form_factor.polymer_micelle': ['*.so', '*.pyd', '*.dll'],
        'form_factor.pringle': ['*.so', '*.pyd', '*.dll'],
        'form_factor.bcc_paracrystal': ['*.so', '*.pyd', '*.dll'],
        'form_factor.fcc_paracrystal': ['*.so', '*.pyd', '*.dll'],
        'structure_factor.hayter_msa': ['*.so', '*.pyd', '*.dll'],
        'structure_factor.hardsphere': ['*.so', '*.pyd', '*.dll'],
    },
)
