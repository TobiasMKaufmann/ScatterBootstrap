import os
from setuptools import setup, Extension, find_packages

# Define the core-shell cylinder C extension module
core_shell_cylinder_module = Extension(
    'core_shell_cylinder.core_shell_cylinder',
    sources=[
        'src/core_shell_cylinder/core_shell_cylinder.c',
        'src/core_shell_cylinder/gauss76.c',
        'src/core_shell_cylinder/polevl.c',
        'src/core_shell_cylinder/sas_J1.c',
        'src/core_shell_cylinder/utils.c'
    ],
    include_dirs=['src/core_shell_cylinder/']
)

# Define the Hayter-MSA C extension module
hayter_msa_module = Extension(
    'core_shell_cylinder.hayter_msa',
    sources=[
        'src/core_shell_cylinder/hayter_msa.c',
        'src/core_shell_cylinder/utils.c'
    ],
    include_dirs=['src/core_shell_cylinder/']
)

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
    ext_modules=[core_shell_cylinder_module, hayter_msa_module],
    packages=find_packages('src'),
    package_dir={'': 'src'},
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