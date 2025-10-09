# ECHEMES Bootstrapping: Advanced Small-Angle Scattering Analysis

A comprehensive Python package for analyzing small-angle scattering (SAS) data using core-shell cylinder models with advanced bootstrapping techniques and high-performance C extensions. The core scattering models are adapted from [SasView](https://www.sasview.org/).

## Features

- **Core-shell cylinder form factors** with fast C implementations
- **Hayter-Penfold MSA structure factors** for charged particles
- **Residuals bootstrapping analysis** for uncertainty quantification
- **Parameter fitting** with robust optimization algorithms
- **Comprehensive visualization tools** for data analysis
- **High-performance C extensions**

## System Requirements

- **Python**: 3.8 or higher
- **C Compiler**: GCC (Linux/macOS) or MSVC (Windows)
- **Operating System**: Linux, macOS, or Windows

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/TobiasMKaufmann/echemes-bootstrapping.git
cd echemes-bootstrapping
```

### 2. System Dependencies

#### Linux (Ubuntu/Debian)
```bash
# Install build essentials and Python development headers
sudo apt update
sudo apt install build-essential python3-dev

# Install HDF5 libraries for full tables support
sudo apt install libhdf5-dev pkg-config
```

#### Linux (CentOS/RHEL/Fedora)
```bash
# Install development tools
sudo yum groupinstall "Development Tools"  # CentOS/RHEL
sudo dnf groupinstall "Development Tools"  # Fedora
sudo yum install python3-devel           # CentOS/RHEL
sudo dnf install python3-devel           # Fedora

# HDF5 support
sudo yum install hdf5-devel              # CentOS/RHEL
sudo dnf install hdf5-devel              # Fedora
```

#### macOS
```bash
# Install Xcode command line tools
xcode-select --install

# Install HDF5 via Homebrew
brew install hdf5
```

#### Windows
- Install **Microsoft Visual Studio Build Tools** or **Visual Studio Community**
- Ensure Python is installed from python.org (includes development headers)

### 3. Python Environment Setup

It's recommended to use a virtual environment:

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # Linux/macOS
# OR
venv\Scripts\activate     # Windows
```

### 4. Install Python Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 5. Build and Install C Extensions

```bash
# Build C extensions in-place
python setup.py build_ext --inplace

# Optional: Install the package in development mode
pip install -e .
```

### 6. Verify Installation

```bash
python -c "
from src.core_shell_cylinder.wrapper import compute_form_factor
from src.core_shell_cylinder.hayter_msa_wrapper import compute_structure_factor
print('C extensions loaded successfully!')
"
```

## Quick Start

### Basic Usage Example

```python
from src.utils import form_factor, structure_factor, intensity
import numpy as np

# Define scattering parameters
q = 0.1  # scattering vector (Å⁻¹)

# Core-shell cylinder parameters
core_sld = 7.7      # core scattering length density
shell_sld = 10.989  # shell scattering length density
solvent_sld = 9.4   # solvent scattering length density
radius = 13.84      # core radius (Å)
thickness = 6.60    # shell thickness (Å)
length = 35.21      # cylinder length (Å)

# Structure factor parameters (Hayter-MSA)
radius_effective = 24.8  # effective radius (Å)
vol_frac = 0.16363      # volume fraction
zz = 28.288             # particle charge
temp = 300              # temperature (K)
csalt = 0.093723        # salt concentration (M)
dialec = 78.3           # dielectric constant

# Calculate form and structure factors
F1, F2 = form_factor(q, core_sld, shell_sld, solvent_sld, radius, thickness, length)
S_q = structure_factor(q, radius_effective, vol_frac, zz, temp, csalt, dialec)

# Total scattering intensity (using the intensity function)
scale = 1.0
background = 0.0
I_q = intensity(q, scale, background, core_sld, shell_sld, solvent_sld, 
                radius, thickness, length, radius_effective, vol_frac, 
                zz, temp, csalt, dialec)

print(f"Form Factor |F(q)|²: {F2:.4f}")
print(f"Structure Factor S(q): {S_q:.4f}")
print(f"Total Intensity I(q): {I_q:.4f}")
```

### Data Analysis Workflow

```python
from src.utils import fit_data, residuals_bootstrap, plot_fit_data, compute_confidence_intervals
import numpy as np

q_exp = np.loadtxt('path/to/data.dat', usecols=0)  # q values
I_exp = np.loadtxt('path/to/data.dat', usecols=1)  # intensity values
# sigma_exp = np.loadtxt('path/to/data.dat', usecols=2)  # error bars (if available)

# Define initial parameters (modify src/initial_params.json for your data)
initial_params = {
    'scale': 1.0,
    'background': 0.1,
    'radius': 15.0,
    'thickness': 5.0,
    'length': 30.0,
    'vol_frac': 0.1,
    'radius_effective': 20.0,
    'zz': 25.0,
    'temp': 300.0,
    'csalt': 0.1,
    'dialec': 78.3
}

# Define which parameters to fit
fit_params = {
    'scale': True,
    'background': True,
    'radius': True,
    'thickness': True,
    'length': True,
    'vol_frac': True,
    'radius_effective': False,
    'zz': False,
    'temp': False,
    'csalt': False,
    'dialec': False
}

# Fit parameters to experimental data
fitted_params, covariance = fit_data(q_exp, I_exp, initial_params, fit_params)

# Perform residuals bootstrap uncertainty analysis
bootstrap_results = residuals_bootstrap(q_exp, I_exp, fitted_params, fit_params, 
                                       n_iterations=1000)

# Compute confidence intervals
confidence_intervals = compute_confidence_intervals(bootstrap_results)

# Visualize results
plot_fit_data(q_exp, I_exp, fitted_params, title="Fitted Data", 
              folder="./results")

print("Fitted parameters:", fitted_params)
print("95% Confidence intervals:", confidence_intervals)
```

## Project Structure

```
├── src/
│   ├── utils.py                           # Main analysis functions (START HERE)
│   ├── data_extraction_functions.py       # Bootstrap results analysis tools
│   ├── data_extraction_example.py         # Usage examples for data extraction
│   ├── fitted_params_table.py             # Parameter validation utilities
│   ├── plot_comparisons.py                # Visualization and comparison tools
│   ├── initial_params.json                # Default parameter configurations
│   ├── core_shell_cylinder/               # High-performance C extensions
│   │   ├── wrapper.py                     # Python wrapper for form factors
│   │   ├── hayter_msa_wrapper.py          # Python wrapper for structure factors
│   │   ├── core_shell_cylinder.c          # C implementation of form factors
│   │   ├── hayter_msa.c                   # C implementation of structure factors
│   │   ├── gauss76.c                      # Gaussian quadrature integration
│   │   ├── sas_J1.c                       # Bessel function implementations
│   │   ├── polevl.c                       # Polynomial evaluation functions
│   │   └── utils.c                        # C utility functions
│   ├── cluster/                           # ETH HPC cluster computing framework
│   │   ├── README.md                      # Complete cluster workflow guide
│   │   ├── process_data.py                # Batch bootstrap processing
│   │   ├── submit_job.sh                  # SLURM job submission script
│   │   ├── setup_cluster.py               # Dependency installation for cluster
│   │   ├── transfer.sh                    # File transfer and job management
│   │   ├── requirements_cluster.txt       # Minimal cluster dependencies
├── requirements.txt                       # Python dependencies
├── setup.py                              # Package installation script
├── pyproject.toml                        # Modern Python package configuration
├── MANIFEST.in                           # Package manifest for distribution
├── CHANGELOG.md                          # Version history and changes
└── README.md                             # This file
```

## Cluster Computing

For computationally intensive bootstrap analyses with thousands of iterations, this package includes a complete cluster computing framework optimized for ETH HPC systems (Euler/Leonhard).

### Quick Start with Cluster

```bash
# Navigate to cluster directory
cd src/cluster

# Edit transfer.sh with your NetHz credentials
nano transfer.sh  # Set CLUSTER_USER="your_nethz"

# Upload files and submit SLURM job
./transfer.sh to

# Monitor job status
./transfer.sh status
./transfer.sh check

# Download results when complete
./transfer.sh retrieve
```

### Cluster Features

- **Automated Workflow**: Single command to upload, build, and submit jobs
- **SLURM Integration**: Optimized resource allocation and job scheduling
- **Remote Monitoring**: Check status, view logs, and track progress remotely
- **Intelligent File Transfer**: Automatic exclusion of unnecessary files
- **Batch Processing**: Process multiple datasets with 5000+ bootstrap iterations
- **HDF5 Output**: Efficient storage of all results in structured format

### Available Commands

- `to` - Upload and submit job
- `retrieve` - Download results (PRIMARY METHOD)
- `status` - Check job queue
- `check` - Comprehensive status with logs
- `logs` - List available log files
- `viewlog JOBID` - View specific job logs
- `clean` - Remove temporary files
- `list` - List all cluster files
- `delete` - Remove all files from cluster

### Typical Workflow

1. **Prepare**: Edit `initial_params.json` with your parameters
2. **Upload**: `./transfer.sh to` submits job to SLURM
3. **Monitor**: `./transfer.sh check` tracks progress
4. **Retrieve**: `./transfer.sh retrieve` downloads HDF5 results
5. **Analyze**: Use `data_extraction_functions.py` for analysis

### Output Structure

Each dataset generates an HDF5 file with:
- Original experimental data (q, I)
- Initial and fitted parameters
- All bootstrap samples (5000 by default)
- 95% confidence intervals
- Metadata (dataset name, processing stage)

For complete documentation, see [`src/cluster/README.md`](src/cluster/README.md).

## Key Dependencies

- **numpy** (≥1.20.0): Numerical computations
- **scipy** (≥1.7.0): Scientific computing and optimization
- **matplotlib** (≥3.3.0): Plotting and visualization
- **pandas** (≥1.3.0): Data manipulation and analysis
- **cffi** (≥1.14.0): C Foreign Function Interface
- **tables** (≥3.6.0): HDF5 data storage support
- **tqdm**: Progress bars for long computations

## Troubleshooting

### Common Installation Issues

1. **C Compiler Not Found**
   ```
   error: Microsoft Visual C++ 14.0 is required
   ```
   **Solution**: Install Visual Studio Build Tools (Windows) or build-essential (Linux)

2. **HDF5 Libraries Missing**
   ```
   error: Could not find HDF5 installation
   ```
   **Solution**: Install HDF5 development libraries (see system dependencies above)

3. **Permission Denied (Linux/macOS)**
   ```
   PermissionError: [Errno 13] Permission denied
   ```
   **Solution**: Use virtual environment or install with `pip install --user`

4. **Import Error After Installation**
   ```
   ImportError: cannot import name 'compute_form_factor'
   ```
   **Solution**: Ensure C extensions built successfully with `python setup.py build_ext --inplace`

### Performance Notes

- C extensions provide 50-100x speedup over pure Python implementations
- For large datasets, consider using the cluster processing scripts in `src/cluster/`
- Bootstrap analysis can be computationally intensive; start with smaller sample sizes for testing

## Development and Contributing

### Running Tests

```bash
python -m pytest tests/  # If tests are available
# OR verify manually:
python src/main.py
```

### Building Documentation

```bash
# If sphinx is installed
cd docs/
make html
```

## Implementing Custom Models

The framework is designed to be easily extensible for implementing other scattering models. The core requirement is to define appropriate intensity and form factor functions that follow the established pattern.

### Required Functions

To implement a new model, you need to create:

1. **`intensity_for_fitting`** - Vectorized intensity function for parameter fitting
2. **`form_factor_for_fitting`** (optional) - Vectorized form factor function when structure factors are negligible

### Implementation Pattern

The framework's flexibility comes from its **dictionary-based parameter system**. The key is to adjust the parameter dictionaries (`initial_params` and `fit_params`) to match your model's requirements. The existing fitting, bootstrapping, and plotting functions will automatically work with any parameter set as long as your model functions accept the corresponding parameters.

**Key Insight**: You primarily need to modify the **dictionaries** passed to functions (like `initial_params` and `fit_params`), rather than the function signatures themselves. Here's how to implement a new model:

#### 1. Define Your Model Functions

```python
# Example: Sphere model implementation
from scipy.special import j1
import numpy as np

def sphere_form_factor(q, radius, sld, solvent_sld):
    """Calculate sphere form factor"""
    contrast = sld - solvent_sld
    qr = q * radius
    # Sphere form factor: 3*(sin(qr) - qr*cos(qr))/qr³
    if qr == 0:
        form_factor = 1.0
    else:
        form_factor = 3.0 * (np.sin(qr) - qr * np.cos(qr)) / (qr**3)
    
    volume = (4.0/3.0) * np.pi * radius**3
    return contrast**2 * volume**2 * form_factor**2

def sphere_intensity(q, scale, background, radius, sld, solvent_sld, 
                    radius_effective=None, vol_frac=None, **structure_params):
    """Calculate total sphere scattering intensity"""
    form_factor_sq = sphere_form_factor(q, radius, sld, solvent_sld)
    
    # Optional: Add structure factor if parameters provided
    if radius_effective is not None and vol_frac is not None:
        # Use your preferred structure factor (e.g., hard sphere, Hayter-MSA)
        S_q = your_structure_factor(q, radius_effective, vol_frac, **structure_params)
        return scale * form_factor_sq * S_q + background
    else:
        return scale * form_factor_sq + background

# Create vectorized versions for fitting
sphere_intensity_for_fitting = np.vectorize(
    sphere_intensity, 
    excluded=['scale', 'background', 'radius', 'sld', 'solvent_sld']
)

sphere_form_factor_for_fitting = np.vectorize(
    lambda q, scale, background, radius, sld, solvent_sld: 
        scale * sphere_form_factor(q, radius, sld, solvent_sld) + background,
    excluded=['scale', 'background', 'radius', 'sld', 'solvent_sld']
)
```

#### 2. Update Parameter Configurations

Create or modify the initial parameters JSON file for your model:

```json
{
    "sphere_model": {
        "scale": 1.0,
        "background": 0.001,
        "radius": 50.0,
        "sld": 4.0,
        "solvent_sld": 6.3,
        "radius_effective": 60.0,
        "vol_frac": 0.1
    }
}
```

#### 3. Adjust Parameter Dictionaries

The most important step is to create parameter dictionaries that match your model:

```python
# Example: Sphere model parameters
sphere_initial_params = {
    "scale": 1.0,
    "background": 0.001,
    "radius": 50.0,         # Different from core_shell_cylinder's radius + thickness
    "sld": 4.0,             # Different parameter name
    "solvent_sld": 6.3,     # Same as core_shell_cylinder
    "radius_effective": 60.0,  # For structure factor
    "vol_frac": 0.1,        # For structure factor
    "zz": 20.0,             # For structure factor
    "temp": 300.0,          # For structure factor
    "csalt": 0.1,           # For structure factor
    "dialec": 78.3          # For structure factor
}

sphere_fit_params = {
    "scale": True,          # Fit this parameter
    "background": True,     # Fit this parameter
    "radius": True,         # Fit this parameter
    "sld": True,            # Fit this parameter
    "solvent_sld": False,   # Keep this fixed
    "radius_effective": False,  # Keep this fixed
    "vol_frac": False,      # Keep this fixed
    "zz": False,            # Keep this fixed
    "temp": False,          # Keep this fixed
    "csalt": False,         # Keep this fixed
    "dialec": False         # Keep this fixed
}

# Use with existing functions - no modification needed!
fitted_params, covariance = fit_data(x_data, y_data, 
                                    initial_params=sphere_initial_params,
                                    fit_params=sphere_fit_params)

bootstrap_results = residuals_bootstrap(x_data, y_data, 
                                       all_params=sphere_initial_params,
                                       fit_params=sphere_fit_params,
                                       n_iterations=1000)
```

#### 4. Optional: Switch Between Models

If you want to support multiple models, you can create a simple model selector:

```python
def get_model_functions_and_params(model_type):
    """Return appropriate functions and default parameters for different models"""
    
    if model_type == "sphere":
        sphere_fit_params = {
            "scale": True, "background": True, "radius": True, "sld": True,
            "solvent_sld": False, "radius_effective": False, "vol_frac": False,
            "zz": False, "temp": False, "csalt": False, "dialec": False
        }
        return (sphere_intensity_for_fitting, sphere_form_factor_for_fitting, 
                sphere_initial_params, sphere_fit_params)
    
    elif model_type == "core_shell_cylinder":
        cylinder_fit_params = {
            "scale": True, "background": True, "radius": True, 
            "thickness": True, "length": True, "core_sld": False,
            "shell_sld": False, "solvent_sld": False
        }
        return (intensity_for_fitting, form_factor_for_fitting,
                initial_params, cylinder_fit_params)
    
    else:
        raise ValueError(f"Unknown model type: {model_type}")

# Usage
model_funcs = get_model_functions_and_params("sphere")
intensity_func, form_factor_func, default_params, default_fit_params = model_funcs
```

### Key Design Principles

1. **Dictionary-Driven Parameters**: The primary customization happens through modifying the `initial_params` and `fit_params` dictionaries to match your model's parameter names and values

2. **Automatic Parameter Passing**: The framework automatically unpacks these dictionaries as `**kwargs` to your model functions

3. **Vectorization**: Use `np.vectorize()` with appropriate `excluded` parameters for fitting functions

4. **Modular Structure**: Separate form factors, structure factors, and intensity calculations

5. **Parameter Dictionary Management**: Simply adjust the parameter dictionaries - no need to modify function signatures

### Example: Adding a Cylinder Model

```python
def cylinder_form_factor(q, radius, length, sld, solvent_sld):
    """Cylinder form factor calculation"""
    contrast = sld - solvent_sld
    volume = np.pi * radius**2 * length
    
    # Cylinder form factor integration over orientations
    # (simplified - actual implementation requires numerical integration)
    qr = q * radius
    ql = q * length
    
    if qr == 0 and ql == 0:
        form_factor = 1.0
    else:
        # Simplified cylinder form factor
        form_factor = (2.0 * j1(qr) / qr)**2 * (np.sin(ql/2) / (ql/2))**2
    
    return contrast**2 * volume**2 * form_factor

# Define intensity, vectorized versions, and parameter files similarly...
```

### Parameter File Structure

Your `initial_params.json` should include all model parameters:

```json
{
    "model_name": {
        "scale": 1.0,
        "background": 0.001,
        "param1": value1,
        "param2": value2,
        "structure_factor_param1": value3,
        "structure_factor_param2": value4
    }
}
```

### Integration with Existing Framework

**The key advantage**: The existing `fit_data()`, `residuals_bootstrap()`, and plotting functions will work automatically with your new model without any modification! You just need to:

1. **Create your model functions** that accept parameters as individual arguments
2. **Create vectorized versions** using `np.vectorize()` 
3. **Define appropriate parameter dictionaries** (`initial_params` and `fit_params`) that match your model's parameter names
4. **Update parameter configuration JSON files** for persistent storage
5. **Ensure your functions return the expected data types** (floats/arrays)

**Example: Complete workflow with sphere model**

```python
# 1. Your model is implemented (sphere_intensity_for_fitting, etc.)
# 2. Define parameters for your specific dataset
my_sphere_params = {
    "scale": 0.8,
    "background": 0.005,
    "radius": 45.0,
    "sld": 3.5,
    "solvent_sld": 6.3,
    # ... structure factor params if needed
}

my_fit_params = {
    "scale": True,
    "radius": True,
    "sld": True,
    "background": False,
    "solvent_sld": False
}

# 3. Use existing framework functions unchanged!
fitted_params, cov = fit_data(q_data, I_data, my_sphere_params, my_fit_params)
bootstrap_results = residuals_bootstrap(q_data, I_data, my_sphere_params, my_fit_params)
plot_fit_data(q_data, I_data, fitted_params)
```

**The framework automatically**:
- Unpacks your parameter dictionaries as `**kwargs` 
- Passes them to your model functions
- Handles the fitting optimization
- Performs bootstrap resampling
- Generates all plots and statistics

This flexible, dictionary-driven design allows you to implement any scattering model while leveraging the existing bootstrapping, fitting, and visualization infrastructure without modifying the core framework code.

## License

MIT License - see [LICENSE](LICENSE) file for details.

**Note**: The core scattering models in `src/core_shell_cylinder/` are adapted from [SasView](https://www.sasview.org/) and are subject to SasView's BSD 3-Clause License. All C source files contain appropriate attribution headers.

## Citation

If you use this software in your research, please cite:

```bibtex
@software{echemes_bootstrapping,
  title = {ECHEMES Bootstrapping: Advanced SAS Analysis Tools},
  author = {Tobias Kaufmann},
  year = {2025},
  url = {https://github.com/TobiasMKaufmann/echemes-bootstrapping},
  version = {0.3.0}
}
```

## Contact

- **Author**: Tobias Kaufmann
- **Email**: tkaufman@student.ethz.ch
- **Repository**: https://github.com/TobiasMKaufmann/echemes-bootstrapping

---

**Note**: This package is designed for scientific research in small-angle scattering analysis. The main analysis functionality is contained in `src/utils.py`, which provides comprehensive tools for bootstrapping, parameter fitting, and uncertainty analysis.
