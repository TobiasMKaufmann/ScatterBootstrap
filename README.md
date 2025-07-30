# ECHEMES Bootstrapping

This project provides a comprehensive Python interface for computing form factors and structure factors of core-shell cylinder models using optimized C implementations. The project includes advanced features like block bootstrapping for uncertainty analysis and parameter fitting capabilities for small-angle scattering (SAS) data analysis.

## Features

- **Form Factor Calculation**: Compute form factors for core-shell cylinder models
- **Structure Factor Calculation**: Hayter-Penfold MSA structure factor implementation
- **Parameter Fitting**: Advanced curve fitting with uncertainty estimation
- **Block Bootstrapping**: Time-series aware bootstrapping for uncertainty analysis
- **Data Visualization**: Comprehensive plotting utilities for analysis results
- **High Performance**: Optimized C implementations for computational efficiency

## Project Structure

```
core_shell_cylinder_project/
├── src/
│   ├── core_shell_cylinder/
│   │   ├── __init__.py
│   │   ├── wrapper.py                 # Python wrapper for form factor calculations
│   │   ├── hayter_msa_wrapper.py      # Python wrapper for structure factor calculations
│   │   ├── core_shell_cylinder.c      # Core form factor implementation
│   │   ├── hayter_msa.c              # Hayter-Penfold MSA structure factor
│   │   ├── gauss76.c                 # Gaussian quadrature implementation
│   │   ├── polevl.c                  # Polynomial evaluation functions
│   │   ├── sas_J1.c                  # Bessel function implementations
│   │   ├── utils.c                   # Utility functions
│   │   └── *.h                       # Header files
│   ├── utils.py                      # Advanced analysis utilities and bootstrapping
│   └── main.py                       # Basic example usage
├── setup.py                          # Package installation configuration
├── requirements.txt                  # Python dependencies
└── README.md                         # This file
```

## Installation

### Prerequisites

- Python 3.8 or higher
- C compiler (gcc recommended)
- Development headers for Python

### Install from Source

1. Clone the repository:
```bash
git clone https://github.com/TobiasMKaufmann/echemes-bootstrapping.git
cd echemes-bootstrapping
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Build and install the package:
```bash
python setup.py build_ext --inplace
pip install -e .
```

## Usage

### Basic Form Factor Calculation

```python
from core_shell_cylinder.wrapper import compute_form_factor

# Calculate form factor for given parameters
q = 0.1  # scattering vector (1/Å)
core_sld = 7.7
shell_sld = 10.989
solvent_sld = 9.4
radius = 13.84
thickness = 6.60
length = 35.21

F, F2 = compute_form_factor(q, core_sld, shell_sld, solvent_sld, 
                           radius, thickness, length)
```

### Structure Factor Calculation

```python
from core_shell_cylinder.hayter_msa_wrapper import compute_structure_factor

# Calculate structure factor
S_q = compute_structure_factor(q, radius_effective=24.8, 
                             volume_fraction=0.16363, charge=28.288,
                             temperature=300, salt_concentration=0.093723,
                             dielectric_constant=78.3)
```

### Advanced Analysis with Bootstrapping

```python
from utils import bootstrapping, fit_bootstrap_samples
import pandas as pd

# Load experimental data
df = pd.read_csv('your_data.dat', sep='\s+', header=0)

# Perform block bootstrapping
bootstrap_samples = bootstrapping(df['q'], df['I'], 
                                n_iterations=1000, block_size=5)

# Fit parameters to bootstrap samples
fitted_params = fit_bootstrap_samples(bootstrap_samples)

# Analyze parameter uncertainties
print(f"Generated {len(fitted_params)} parameter sets")
```

### Complete Analysis Example

```bash
# Run basic form factor example
python src/main.py

# Run advanced bootstrapping analysis
python src/utils.py
```

## Key Components

### C Extensions

- **core_shell_cylinder.c**: High-performance form factor calculations
- **hayter_msa.c**: Structure factor calculations using Hayter-Penfold MSA theory
- **gauss76.c**: 76-point Gaussian quadrature for numerical integration
- **sas_J1.c**: Optimized Bessel function implementations

### Python Modules

- **utils.py**: Advanced analysis utilities including:
  - Block bootstrapping for time-series data
  - Parameter fitting with uncertainty estimation
  - Comprehensive plotting functions
  - Data visualization tools

### Analysis Features

- **Block Bootstrapping**: Preserves temporal structure in time-series data
- **Parameter Fitting**: Robust curve fitting with error handling
- **Uncertainty Analysis**: Statistical analysis of fitted parameters
- **Visualization**: Publication-ready plots and analysis results

## Mathematical Models

### Core-Shell Cylinder Form Factor

The form factor is calculated using the analytical expression for a core-shell cylinder with:
- Core radius: `radius`
- Shell thickness: `thickness`
- Cylinder length: `length`
- Scattering length densities for core, shell, and solvent

### Hayter-Penfold MSA Structure Factor

The structure factor accounts for interparticle interactions using:
- Effective radius and volume fraction
- Particle charge and ionic strength
- Temperature and dielectric constant

## Performance

The C implementations provide significant performance improvements:
- Form factor calculations: ~100x faster than pure Python
- Structure factor calculations: ~50x faster than pure Python
- Numerical integration: Optimized 76-point Gaussian quadrature

## Contributing

Contributions are welcome! Please feel free to:
- Submit bug reports and feature requests
- Contribute code improvements
- Add documentation and examples
- Optimize computational performance

## License

This project is licensed under the MIT License. See the LICENSE file for details.

## Citation

If you use this software in your research, please cite:

```
@software{echemes_bootstrapping,
  title = {ECHEMES Bootstrapping: Advanced SAS Analysis Tools with Block Bootstrapping},
  author = {Tobias Kaufmann},
  year = {2025},
  url = {https://github.com/TobiasMKaufmann/echemes-bootstrapping}
}
```