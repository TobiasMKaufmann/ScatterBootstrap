# ECHEMES Bootstrapping

## Overview
This project provides advanced tools for small-angle scattering (SAS) analysis, focusing on core-shell cylinder models with comprehensive uncertainty analysis through block bootstrapping.

## Recent Updates
- Added Hayter-Penfold MSA structure factor calculations
- Implemented block bootstrapping for time-series analysis
- Enhanced parameter fitting with uncertainty estimation
- Added comprehensive visualization tools
- Improved C extension performance

## Quick Start

### Installation
```bash
git clone https://github.com/TobiasMKaufmann/echemes-bootstrapping.git
cd echemes-bootstrapping
pip install -r requirements.txt
python setup.py build_ext --inplace
```

### Basic Usage
```python
from core_shell_cylinder.wrapper import compute_form_factor
from core_shell_cylinder.hayter_msa_wrapper import compute_structure_factor

# Form factor calculation
F, F2 = compute_form_factor(q=0.1, core_sld=7.7, shell_sld=10.989, 
                           solvent_sld=9.4, radius=13.84, thickness=6.60, length=35.21)

# Structure factor calculation  
S_q = compute_structure_factor(q=0.1, radius_effective=24.8, volume_fraction=0.16363,
                              charge=28.288, temperature=300, salt_concentration=0.093723,
                              dielectric_constant=78.3)
```

### Advanced Analysis
```python
from utils import bootstrapping, fit_bootstrap_samples

# Load data and perform bootstrapping analysis
bootstrap_samples = bootstrapping(x_data, y_data, n_iterations=1000, block_size=5)
fitted_params = fit_bootstrap_samples(bootstrap_samples)
```

## Project Structure
- `src/core_shell_cylinder/`: C extensions and Python wrappers
- `src/utils.py`: Advanced analysis utilities and bootstrapping
- `src/main.py`: Basic usage examples
- `setup.py`: Package configuration
- `requirements.txt`: Dependencies

## Key Features
- High-performance C implementations
- Block bootstrapping for uncertainty analysis
- Parameter fitting with error estimation
- Comprehensive data visualization
- Time-series aware resampling

## Development
This project uses modern Python packaging standards with both `setup.py` and `pyproject.toml` for maximum compatibility.

For development installation:
```bash
pip install -e .[dev]
```

## License
MIT License - see LICENSE file for details.
