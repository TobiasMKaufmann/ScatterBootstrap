import os
import sys
import subprocess
from setuptools import setup, find_packages
from setuptools.command.build_py import build_py

class BuildSharedLibraries(build_py):
    """Custom build command to compile C files as shared libraries"""
    
    def run(self):
        # Build core_shell_cylinder shared library
        self.build_shared_lib(
            'core_shell_cylinder',
            [
                'src/core_shell_cylinder/core_shell_cylinder.c',
                'src/core_shell_cylinder/gauss76.c',
                'src/core_shell_cylinder/polevl.c',
                'src/core_shell_cylinder/sas_J1.c',
                'src/core_shell_cylinder/utils.c'
            ]
        )
        
        # Build hayter_msa shared library
        self.build_shared_lib(
            'hayter_msa',
            [
                'src/core_shell_cylinder/hayter_msa.c',
                'src/core_shell_cylinder/utils.c'
            ]
        )
        
        # Continue with the normal build
        build_py.run(self)
    
    def build_shared_lib(self, name, sources):
        """Build a shared library from C sources"""
        output_dir = 'src/core_shell_cylinder'
        os.makedirs(output_dir, exist_ok=True)
        
        if sys.platform == 'win32':
            # Windows with MSVC - build as DLL, then rename to .pyd
            dll_file = os.path.join(output_dir, f'{name}.dll')
            output_file = os.path.join(output_dir, f'{name}.pyd')
            
            # Convert paths to Windows format
            output_dir_win = output_dir.replace('/', '\\')
            
            # Object files - create them in the output directory
            obj_files = []
            for src in sources:
                # Extract just the filename and change extension
                base_name = os.path.basename(src).replace('.c', '.obj')
                obj = os.path.join(output_dir, base_name)
                obj_files.append(obj)
            
            try:
                # Compile each source file separately
                for src, obj in zip(sources, obj_files):
                    # Convert paths to Windows format
                    src_win = src.replace('/', '\\')
                    obj_win = obj.replace('/', '\\')
                    
                    compile_cmd = [
                        'cl', '/c', '/nologo', '/O2', '/MD', '/W3',
                        f'/I{output_dir_win}',
                        f'/Tc{src_win}',
                        f'/Fo{obj_win}'
                    ]
                    print(f"Compiling {src}...")
                    subprocess.run(compile_cmd, check=True)
                
                # Link object files into DLL
                obj_files_win = [obj.replace('/', '\\') for obj in obj_files]
                dll_file_win = dll_file.replace('/', '\\')
                
                link_cmd = [
                    'link', '/DLL', '/nologo',
                    f'/OUT:{dll_file_win}'
                ]
                link_cmd.extend(obj_files_win)
                
                print(f"Linking {name}.dll...")
                subprocess.run(link_cmd, check=True)
                
                # Rename .dll to .pyd for ctypes compatibility
                if os.path.exists(dll_file):
                    if os.path.exists(output_file):
                        os.remove(output_file)
                    os.rename(dll_file, output_file)
                    print(f"Renamed {dll_file} -> {output_file}")
                
            finally:
                # Clean up intermediate files (even if build fails)
                for obj in obj_files:
                    if os.path.exists(obj):
                        os.remove(obj)
                lib_file = dll_file.replace('.dll', '.lib')
                exp_file = dll_file.replace('.dll', '.exp')
                if os.path.exists(lib_file):
                    os.remove(lib_file)
                if os.path.exists(exp_file):
                    os.remove(exp_file)
        else:
            # Linux/Mac with GCC
            output_file = os.path.join(output_dir, f'{name}.so')
            compile_cmd = ['gcc', '-shared', '-fPIC', '-O2']
            compile_cmd.extend([f'-I{output_dir}'])
            compile_cmd.extend(sources)
            compile_cmd.extend(['-o', output_file, '-lm'])
        
            print(f"Building {name}: {' '.join(compile_cmd)}")
            subprocess.run(compile_cmd, check=True)
        
        print(f"Successfully built {output_file}")

# Setup function
setup(
    name='core_shell_cylinder_project',
    version='0.3.0',
    description='Advanced SAS analysis with bootstrapping, cluster computing, and high-performance C extensions for core-shell cylinder models.',
    long_description=open('README.md', encoding='utf-8').read() if os.path.exists('README.md') else '',
    long_description_content_type='text/markdown',
    author='Tobias Kaufmann',
    author_email='tkaufman@student.ethz.ch',
    url='https://github.com/TobiasMKaufmann/echemes-bootstrapping',
    cmdclass={'build_py': BuildSharedLibraries},
    packages=find_packages('src'),
    package_dir={'': 'src'},
    package_data={
        'core_shell_cylinder': ['*.so', '*.pyd', '*.dll'],
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