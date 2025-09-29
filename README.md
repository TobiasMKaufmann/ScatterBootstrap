# ECHEMES Bootstrapping

This project provides advanced analysis tools for small-angle scattering (SAS) data. **The most relevant features are in `utils.py`**, which contains all the main analysis, bootstrapping, fitting, and visualization functions. Other components support performance optimization through C extensions.

## Key Components

- **`src/utils.py`**: Main analysis module containing block bootstrapping, parameter fitting, uncertainty analysis, and plotting functions
- **C Extensions**: Fast form/structure factor calculations for core-shell cylinder models
- **Installation**: Standard Python package with C extension building

## Installation

- Python 3.8+, C compiler (gcc)
- Install: `pip install -r requirements.txt` then `python setup.py build_ext --inplace`
- Test: `python test_install.py`

## Usage

- **Main Analysis**: Use functions in `src/utils.py` for bootstrapping, fitting, and plotting
- **Fast Calculations**: C extension wrappers in `src/core_shell_cylinder/` for form/structure factors

## Features Summary

- **Block bootstrapping** and **parameter fitting** with uncertainty analysis  
- **Core-shell cylinder** form factors and **Hayter-Penfold MSA** structure factors
- **C extensions** for major performance improvements (~50-100x speedup)

## License & Citation

MIT License. If used in research, cite as:
```
@software{echemes_bootstrapping,
  title = {ECHEMES Bootstrapping: Advanced SAS Analysis Tools},
  author = {Tobias Kaufmann},
  year = {2025},
  url = {https://github.com/TobiasMKaufmann/echemes-bootstrapping}
}
```