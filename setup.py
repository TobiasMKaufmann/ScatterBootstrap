import os
import sys
import subprocess
from setuptools import setup, find_packages
from setuptools.command.build_py import build_py

class BuildSharedLibraries(build_py):
    """Custom build command to compile C files as shared libraries"""
    
    def run(self):
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
                    
                    compile_cmd = [
                        'cl', '/c', '/nologo', '/O2', '/MD', '/W3', '/DFLOAT_SIZE=8', '/favor:ARM64',
                        f'/I{output_dir_win}',
                        f'/I{lib_dir_win}',
                        f'/Tc{src_win}',
                        f'/Fo{obj_win}'
                    ]
                    subprocess.run(compile_cmd, check=True)
                
                # Link
                obj_files_win = [obj.replace('/', '\\') for obj in obj_files]
                dll_file_win = dll_file.replace('/', '\\')
                
                link_cmd = [
                    'link', '/DLL', '/nologo',
                    f'/OUT:{dll_file_win}',
                    f'/IMPLIB:{lib_file}'
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
                
                link_cmd.extend(obj_files_win)
                
                if link_to_sas_core:
                    sas_core_lib = os.path.abspath('src\\lib\\libsas_core.lib')
                    if os.path.exists(sas_core_lib):
                        link_cmd.append(sas_core_lib)
                    else:
                        print(f"  Warning: libsas_core.lib not found at {sas_core_lib}, linking may fail")
                
                subprocess.run(link_cmd, check=True)
                
                if os.path.exists(dll_file):
                    if os.path.exists(output_file):
                        os.remove(output_file)
                    os.rename(dll_file, output_file)
                
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
        
        print(f"  ✓ Successfully built {output_file}")

# Setup function
setup(
    name='core_shell_cylinder_project',
    version='0.3.0',
    description='Advanced SAS analysis with bootstrapping, cluster computing, and high-performance C extensions for multiple scattering models.',
    long_description=open('README.md', encoding='utf-8').read() if os.path.exists('README.md') else '',
    long_description_content_type='text/markdown',
    author='Tobias Kaufmann',
    author_email='tkaufman@student.ethz.ch',
    url='https://github.com/TobiasMKaufmann/echemes-bootstrapping',
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
    install_requires=[
        'numpy>=1.20.0',
        'scipy>=1.7.0',
        'matplotlib>=3.3.0',
        'pandas>=1.3.0',
        'cffi>=1.14.0',
        'tables>=3.6.0',
        'tqdm>=4.60.0'
    ],
    python_requires='>=3.8',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Topic :: Scientific/Engineering :: Physics',
        'Topic :: Scientific/Engineering :: Chemistry',
    ],
    keywords='scattering, form factor, structure factor, small angle scattering, SAS, SAXS, SANS, bootstrapping, cluster computing, uncertainty quantification',
)
