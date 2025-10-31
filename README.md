# ECHEMES Bootstrapping: Advanced Small-Angle Scattering Analysis

A comprehensive Python package for analyzing small-angle scattering (SAS) data with **14 form factor models** and **2 structure factor models**, featuring advanced bootstrapping techniques and high-performance cross-platform C extensions. All scattering models are adapted from [SasView](https://www.sasview.org/) with optimized implementations.

## Features

### Multi-Model Support
- **14 Form Factor Models**: Sphere, Ellipsoid, Cylinder variants (core-shell, elliptical), Barbell, Fuzzy Sphere, Onion, Linear Pearls, Lamellar HG, Polymer Micelle, Pringle, Core Multi-Shell, and Paracrystal lattices (BCC, FCC)
- **2 Structure Factor Models**: Hayter-MSA (charged particles) and Hard Sphere interactions
- **Modular Architecture**: Easy integration of new scattering models

### Cross-Platform Performance
- **Windows MSVC Support**: Automatic detection and configuration of Microsoft Visual C++ compiler
- **Linux/macOS GCC**: Optimized builds with proper RPATH configuration
- **Shared Core Library**: Single `libsas_core` library for common functions (Bessel, quadrature, polynomials)
- **50-100x Speedup**: High-performance C implementations vs. pure Python

### Advanced Analysis
- **Residuals Bootstrapping**: Comprehensive uncertainty quantification
- **Robust Fitting**: Multiple optimization algorithms with parameter bounds
- **HDF5 Data Storage**: Efficient batch processing and result management
- **Cluster Computing**: ETH HPC integration for large-scale analyses

### Developer-Friendly
- **Automatic Build System**: Smart detection of compilers and dependencies
- **Extensible Design**: Dictionary-driven parameter system for custom models
- **Comprehensive Documentation**: Detailed examples and API reference

## System Requirements

- **Python**: 3.8 or higher
- **C Compiler**: 
  - **Windows**: Microsoft Visual C++ 14.0+ (Visual Studio Build Tools 2019/2022 or Visual Studio Community)
  - **Linux**: GCC (via `build-essential` package)
  - **macOS**: Clang (via Xcode Command Line Tools)
- **Operating System**: Windows 10/11, Linux (Ubuntu/Debian/RHEL/CentOS), macOS 10.14+

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

**Option 1: Visual Studio Build Tools (Recommended)**

1. Download and install [Microsoft C++ Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/)
2. During installation, select:
   - "Desktop development with C++"
   - Ensure "MSVC v142+" and "Windows 10/11 SDK" are checked
3. Restart your terminal/IDE after installation

**Option 2: Visual Studio Community**

Install [Visual Studio Community](https://visualstudio.microsoft.com/vs/community/) with the "Desktop development with C++" workload.

**Verification:**
```cmd
cl
```
Should show the MSVC compiler version. If not, the build system will automatically locate and configure it.

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

The build system automatically detects your platform and compiler:

**All Platforms:**
```bash
# Build all form factor and structure factor models
python setup.py build_py

# Verify successful build (should show all 14 form factors + 2 structure factors)
ls src/form_factor/*/*.so       # Linux/macOS
dir src\form_factor\*\*.pyd     # Windows

# Optional: Install package in development mode
pip install -e .
```

**What Gets Built:**
- `libsas_core` - Shared library with Bessel functions, quadrature, and utilities
- **Form Factors**: sphere, ellipsoid, barbell, core_shell_cylinder, core_multi_shell, elliptical_cylinder, fuzzy_sphere, lamellar_hg, linear_pearls, onion, polymer_micelle, pringle, bcc_paracrystal, fcc_paracrystal
- **Structure Factors**: hayter_msa, hardsphere

**Build System Features:**
- Automatic MSVC detection and configuration on Windows
- Proper RPATH settings on Linux/macOS for library dependencies
- Intelligent function export detection
- Parallel compilation support

### 6. Verify Installation

```bash
# Quick test of the build
python src/utils.py

# Should output scattering calculations and confirm all models loaded successfully
```

## Available Models

### Form Factors (14 Models)

The package includes comprehensive form factor implementations for various particle geometries:

| Model | Description | Key Parameters |
|-------|-------------|----------------|
| **sphere** | Homogeneous sphere | `radius`, `sld` |
| **ellipsoid** | Prolate/oblate ellipsoid | `radius_polar`, `radius_equatorial`, `sld` |
| **core_shell_cylinder** | Cylinder with shell coating | `radius`, `thickness`, `length`, `core_sld`, `shell_sld` |
| **barbell** | Dumbbell-shaped particles | `radius_bell`, `radius`, `length` |
| **core_multi_shell** | Multi-layer spherical shells | `radius`, `thickness[N]`, `sld[N]` |
| **elliptical_cylinder** | Cylinder with elliptical cross-section | `radius_minor`, `axis_ratio`, `length` |
| **fuzzy_sphere** | Sphere with fuzzy interface | `radius`, `fuzziness`, `sld` |
| **lamellar_hg** | Head-group bilayer | `tail_length`, `head_length`, `sld_head`, `sld_tail` |
| **linear_pearls** | Linear chain of spheres | `radius`, `num_pearls`, `edge_sep` |
| **onion** | Multi-shell sphere (onion model) | `radius`, `thickness[N]`, `sld[N]` |
| **polymer_micelle** | Star polymer micelle | `radius_core`, `radius_gyr`, `sld_core`, `sld_corona` |
| **pringle** | Hyperbolic paraboloid | `radius`, `thickness`, `alpha`, `beta` |
| **bcc_paracrystal** | Body-centered cubic lattice | `radius`, `dnn`, `d_factor` |
| **fcc_paracrystal** | Face-centered cubic lattice | `radius`, `dnn`, `d_factor` |

### Structure Factors (2 Models)

Interparticle interference effects for concentrated systems:

| Model | Description | Key Parameters |
|-------|-------------|----------------|
| **hayter_msa** | Hayter-Penfold MSA for charged particles | `radius_effective`, `vol_frac`, `charge`, `temp`, `salt_conc`, `dielectric` |
| **hardsphere** | Hard sphere repulsion | `radius_effective`, `vol_frac` |

### Model Architecture

All models follow a modular design:
- **C Implementation**: High-performance kernel in `src/form_factor/<model>/<model>.c`
- **Python Wrapper**: Easy-to-use interface in `src/form_factor/<model>/wrapper.py`
- **Shared Core**: Common functions (Bessel, quadrature) in `src/lib/libsas_core`
- **Automatic Loading**: Models dynamically loaded based on available compiled libraries

**Adding New Models**: See the "Implementing Custom Models" section below for a complete guide.

## Quick Start

### Basic Usage Example

The framework uses a **modular, dictionary-based** approach for maximum flexibility. You can work with any of the 14 form factor models by simply changing the model configuration in `src/utils.py`.

```python
import sys
sys.path.insert(0, 'src')
from utils import form_factor, structure_factor, intensity
import numpy as np

# Define scattering parameters as keyword arguments
q = 0.1  # scattering vector (Å⁻¹)

# Example: Barbell form factor parameters (default model)
model_params = {
    "sld": 4.0e-6,           # barbell scattering length density
    "solvent_sld": 1.0e-6,   # solvent scattering length density
    "radius_bell": 20.0,     # bell radius (Å)
    "radius": 10.0,          # cylinder radius (Å)
    "length": 50.0           # cylinder length (Å)
}

# Structure factor parameters (Hayter-MSA for charged particles)
structure_params = {
    "radius_effective": 24.8,    # effective radius (Å)
    "volfraction": 0.16363,      # volume fraction
    "charge": 28.288,            # particle charge
    "temperature": 300,          # temperature (K)
    "saltconc": 0.093723,        # salt concentration (M)
    "dielectconst": 78.3         # dielectric constant
}

# Calculate form factor (returns F² directly)
F2 = form_factor(q, **model_params)

# Calculate structure factor
S_q = structure_factor(q, **structure_params)

# Total scattering intensity with scaling
scale = 1.0
background = 0.001
I_q = intensity(q, scale, background, **model_params, **structure_params)

print(f"Form Factor F²(q): {F2:.6e}")
print(f"Structure Factor S(q): {S_q:.4f}")
print(f"Total Intensity I(q): {I_q:.6e}")
```

**Switching Models**: To use a different form factor (e.g., `sphere`, `core_shell_cylinder`, `ellipsoid`), edit the configuration at the top of `src/utils.py`:

```python
# In src/utils.py, lines 73-75
FORM_FACTOR_MODEL = "sphere"  # Change to any of 14 available models
STRUCTURE_FACTOR_MODEL = "hayter_msa"  # or "hardsphere"
```

Then adjust the `initial_params` and `fit_params` dictionaries (lines 213-240) to match your chosen model's parameters.

### Data Analysis Workflow

The framework provides a complete pipeline for fitting experimental data and quantifying uncertainties through bootstrap resampling.

```python
import sys
sys.path.insert(0, 'src')
from utils import fit_data, residuals_bootstrap, compute_confidence_intervals, plot_fit_data
import numpy as np

# Load experimental data
q_exp = np.loadtxt('path/to/data.dat', usecols=0)  # q values (Å⁻¹)
I_exp = np.loadtxt('path/to/data.dat', usecols=1)  # intensity values
# sigma_exp = np.loadtxt('path/to/data.dat', usecols=2)  # uncertainties (optional)

# Define initial parameter guesses (customize for your model and data)
initial_params = {
    "scale": 1.0,
    "background": 0.001,
    "sld": 4.0e-6,
    "solvent_sld": 1.0e-6,
    "radius_bell": 20.0,      # Barbell-specific
    "radius": 10.0,
    "length": 50.0,
    "radius_effective": 24.8,  # Structure factor
    "volfraction": 0.16,
    "charge": 28.0,
    "temperature": 300.0,
    "saltconc": 0.1,
    "dielectconst": 78.3
}

# Define which parameters to fit (True) vs. keep fixed (False)
fit_params = {
    "scale": True,
    "background": True,
    "sld": True,
    "solvent_sld": False,     # Often kept fixed
    "radius_bell": True,
    "radius": True,
    "length": True,
    "radius_effective": True,
    "volfraction": True,
    "charge": True,
    "temperature": False,      # Usually kept fixed
    "saltconc": True,
    "dielectconst": False      # Usually kept fixed
}

# Step 1: Fit experimental data
print("Fitting data...")
fitted_params, covariance, param_order = fit_data(
    q_exp, I_exp, 
    initial_params=initial_params, 
    fit_params=fit_params
)

# Convert fitted parameters array back to dictionary
fitted_dict = {key: fitted_params[i] for i, key in enumerate(param_order)}
# Add fixed parameters
for key, value in initial_params.items():
    if key not in fitted_dict:
        fitted_dict[key] = value

print("Fitted parameters:")
for key, value in fitted_dict.items():
    if fit_params.get(key, False):
        print(f"  {key}: {value:.6e}")

# Step 2: Bootstrap uncertainty quantification
print("\nPerforming bootstrap analysis...")
bootstrap_results = residuals_bootstrap(
    q_exp, I_exp, 
    all_params=fitted_dict,      # Use fitted values as starting point
    fit_params=fit_params,
    n_iterations=1000,           # Increase for better statistics
    use_structure_factor=True    # Set False if no structure factor
)

# Step 3: Compute confidence intervals
confidence_intervals = compute_confidence_intervals(bootstrap_results, confidence_level=0.95)

print("\n95% Confidence Intervals:")
for param, (lower, upper) in confidence_intervals.items():
    mean_val = np.mean(bootstrap_results[param])
    print(f"  {param}: {mean_val:.6e} [{lower:.6e}, {upper:.6e}]")

# Step 4: Visualize results
print("\nGenerating plots...")
plot_fit_data(
    q_exp, I_exp, 
    all_params=fitted_dict,
    title="Barbell Model Fit",
    folder="./results",          # Output directory
    use_structure_factor=True
)

print("Analysis complete! Results saved to ./results/")
```

**Key Functions:**

- **`fit_data()`**: Non-linear least squares fitting using scipy's Levenberg-Marquardt algorithm
- **`residuals_bootstrap()`**: Resamples residuals to quantify parameter uncertainties
- **`compute_confidence_intervals()`**: Calculates percentile-based confidence intervals
- **`plot_fit_data()`**: Creates publication-ready plots with fit overlays and residuals

**Performance Tips:**

- Start with `n_iterations=100` for testing, increase to 1000-5000 for final analysis
- Use the cluster computing framework (`src/cluster/`) for large bootstrap analyses
- Set `use_structure_factor=False` if structure factor effects are negligible

## Project Structure

```
echemes-bootstrapping/
├── src/
│   ├── utils.py                           # Main analysis functions (START HERE)
│   ├── data_extraction_functions.py       # Bootstrap results analysis tools
│   ├── data_extraction_example.py         # Usage examples for data extraction
│   ├── fitted_params_table.py             # Parameter validation utilities
│   ├── plot_comparisons.py                # Visualization and comparison tools
│   ├── initial_params.json                # Default parameter configurations
│   │
│   ├── lib/                               # Shared C library components
│   │   ├── libsas_core.so/.pyd/.dll       # Compiled shared library
│   │   ├── libsas_core.lib                # Import library (Windows)
│   │   ├── sas_J1.c/h                     # Bessel J1 functions
│   │   ├── sas_J0.c/h                     # Bessel J0 functions
│   │   ├── sas_JN.c/h                     # Bessel Jn functions
│   │   ├── sas_3j1x_x.c                   # 3*j1(x)/x function
│   │   ├── gauss76.c/h                    # 76-point Gauss quadrature
│   │   ├── gauss150.c/h                   # 150-point Gauss quadrature
│   │   ├── polevl.c/h                     # Polynomial evaluation
│   │   ├── utils.c/h                      # Math utilities (SINCOS, etc.)
│   │   └── sas_core.h                     # Common header and constants
│   │
│   ├── form_factor/                       # Form factor models (14 models)
│   │   ├── __init__.py
│   │   ├── sphere/
│   │   │   ├── __init__.py
│   │   │   ├── wrapper.py                 # Python interface
│   │   │   ├── sphere.c                   # C implementation
│   │   │   └── sphere.so/.pyd/.dll        # Compiled library
│   │   ├── ellipsoid/                     # [Same structure]
│   │   ├── core_shell_cylinder/           # [Same structure]
│   │   ├── barbell/                       # [Same structure]
│   │   ├── core_multi_shell/              # [Same structure]
│   │   ├── elliptical_cylinder/           # [Same structure]
│   │   ├── fuzzy_sphere/                  # [Same structure]
│   │   ├── lamellar_hg/                   # [Same structure]
│   │   ├── linear_pearls/                 # [Same structure]
│   │   ├── onion/                         # [Same structure]
│   │   ├── polymer_micelle/               # [Same structure]
│   │   ├── pringle/                       # [Same structure]
│   │   ├── bcc_paracrystal/               # [Same structure + sphere_form.c]
│   │   └── fcc_paracrystal/               # [Same structure + sphere_form.c]
│   │
│   ├── structure_factor/                  # Structure factor models (2 models)
│   │   ├── __init__.py
│   │   ├── hayter_msa/
│   │   │   ├── __init__.py
│   │   │   ├── wrapper.py                 # Python interface
│   │   │   ├── hayter_msa.c               # C implementation
│   │   │   └── hayter_msa.so/.pyd/.dll    # Compiled library
│   │   └── hardsphere/                    # [Same structure]
│   │
│   ├── cluster/                           # ETH HPC cluster computing framework
│   │   ├── README.md                      # Complete cluster workflow guide
│   │   ├── process_data.py                # Batch bootstrap processing
│   │   ├── submit_job.sh                  # SLURM job submission script
│   │   ├── setup_cluster.py               # Dependency installation for cluster
│   │   ├── transfer.sh                    # File transfer and job management
│   │   └── requirements_cluster.txt       # Minimal cluster dependencies
│   │
│   └── old/                               # Archived/legacy code
│
├── build/                                 # Build output directory
│   └── lib/                               # Compiled Python modules
│       ├── form_factor/                   # Built form factors
│       └── structure_factor/              # Built structure factors
│
├── requirements.txt                       # Python dependencies
├── setup.py                               # Cross-platform build system with MSVC support
├── pyproject.toml                         # Modern Python package configuration
├── MANIFEST.in                            # Package manifest for distribution
├── LICENSE                                # MIT License
├── CHANGELOG.md                           # Version history and changes
├── RELEASE_NOTES_v0.3.0.md               # Recent release notes
├── EXAMPLE_ADDING_NEW_MODEL.md           # Guide for adding new models
└── README.md                              # This file
```

**Key Directories:**
- **`src/lib/`**: Shared C library used by all models
- **`src/form_factor/`**: Individual form factor implementations (each in its own subdirectory)
- **`src/structure_factor/`**: Structure factor implementations
- **`src/cluster/`**: HPC cluster tools for large-scale analysis
- **`build/lib/`**: Compiled Python packages (created during installation)

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

#### 1. Windows: C Compiler Not Found
```
error: Microsoft Visual C++ 14.0 or greater is required
```
**Solution**: 
- Install [Visual Studio Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/)
- Select "Desktop development with C++" workload
- Restart terminal after installation
- The build system automatically searches these locations:
  - `C:\BuildTools`
  - `C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools`
  - `C:\Program Files (x86)\Microsoft Visual Studio\2019\BuildTools`

**Advanced**: If `cl.exe` is not in PATH, `setup.py` will automatically configure the MSVC environment.

#### 2. Windows: Link Errors or Missing DLL
```
error LNK2001: unresolved external symbol
```
**Solution**: 
- Ensure Windows SDK is installed (included with Build Tools)
- Verify `libsas_core.lib` and `libsas_core.pyd` exist in `src/lib/`
- Rebuild: `python setup.py clean --all && python setup.py build_py`

#### 3. Linux: HDF5 Libraries Missing
#### 3. Linux: HDF5 Libraries Missing
```
error: Could not find HDF5 installation
```
**Solution**: Install HDF5 development libraries:
```bash
sudo apt install libhdf5-dev pkg-config  # Ubuntu/Debian
sudo dnf install hdf5-devel              # Fedora
sudo yum install hdf5-devel              # CentOS/RHEL
```

#### 4. macOS: No C Compiler
```
xcrun: error: invalid active developer path
```
**Solution**: 
```bash
xcode-select --install
```

#### 5. Permission Denied (Linux/macOS)
```
PermissionError: [Errno 13] Permission denied
```
**Solution**: Use virtual environment (recommended) or:
```bash
pip install --user -e .
```

#### 6. Import Error After Installation
```
ImportError: cannot import name 'form_factor'
```
**Solution**: 
- Verify C extensions built: `ls src/form_factor/*/sphere.so` (Linux/macOS) or `dir src\form_factor\sphere\*.pyd` (Windows)
- Rebuild: `python setup.py build_py`
- Check for compilation errors in build output

#### 7. Windows: UNC Path Errors
```
CMD.exe does not support UNC paths as current directories
```
**Solution**: Map network drive to a letter (e.g., `Z:\`) or work from local directory.

### Build System Diagnostics

**Check Build Status:**
```bash
# Verify all models compiled
python -c "from src.form_factor.sphere import wrapper; print('Sphere OK')"
python -c "from src.structure_factor.hayter_msa import wrapper; print('Hayter-MSA OK')"

# List built libraries
ls src/lib/*.so src/form_factor/*/*.so src/structure_factor/*/*.so     # Linux/macOS
dir src\lib\*.pyd src\form_factor\*\*.pyd src\structure_factor\*\*.pyd # Windows
```

**Clean and Rebuild:**
```bash
# Remove all build artifacts
rm -rf build/ src/**/*.so src/**/*.pyd src/**/*.o src/**/*.obj  # Linux/macOS
del /s /q build src\*.so src\*.pyd src\*.o src\*.obj            # Windows

# Rebuild from scratch
python setup.py build_py
```

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

The framework is designed for easy extensibility. You can add new scattering models by following the established pattern used for existing models. The key is understanding the **modular architecture** and **dictionary-based parameter system**.

### Architecture Overview

Each model consists of:

1. **C Implementation** (`model.c`): High-performance scattering calculations
2. **Python Wrapper** (`wrapper.py`): Python interface using ctypes/cffi
3. **Configuration** (`utils.py`): Model selection and parameter definitions
4. **Parameter Dictionaries**: `initial_params` and `fit_params` in `utils.py`

### Step-by-Step: Adding a New Form Factor Model

Let's walk through adding a hypothetical "cylinder" model:

#### 1. Create Model Directory Structure

```bash
mkdir -p src/form_factor/cylinder
cd src/form_factor/cylinder
```

#### 2. Implement C Code (`cylinder.c`)

Create `src/form_factor/cylinder/cylinder.c`:

```c
/*
 * Cylinder form factor implementation
 * Adapted from SasView (https://www.sasview.org/)
 */

#include "../../lib/sas_core.h"
#include <math.h>

// Function to compute cylinder form factor squared
double Iq(double q,
          double sld,
          double solvent_sld,
          double radius,
          double length)
{
    const double contrast = sld - solvent_sld;
    const double volume = M_PI * radius * radius * length;
    
    // Simplified cylinder form factor (averaged over orientations)
    const double qr = q * radius;
    const double ql = q * length / 2.0;
    
    double form_factor;
    if (qr < 1e-6 && ql < 1e-6) {
        form_factor = 1.0;
    } else {
        // Use Bessel J1 from libsas_core
        const double besarg = 2.0 * sas_J1c(qr);  // 2*J1(x)/x
        const double sinc = (ql == 0.0) ? 1.0 : sin(ql) / ql;
        form_factor = besarg * besarg * sinc * sinc;
    }
    
    return 1.0e-4 * contrast * contrast * volume * volume * form_factor;
}

// Volume calculation (useful for structure factor scaling)
double form_volume(double radius, double length)
{
    return M_PI * radius * radius * length;
}

// Effective radius for structure factor
double radius_effective(int mode, double radius, double length)
{
    // Mode 1: radius of a sphere with same volume
    if (mode == 1) {
        return pow(0.75 * radius * radius * length, 1.0/3.0);
    }
    // Default: use cylinder radius
    return radius;
}
```

#### 3. Create Python Wrapper (`wrapper.py`)

Create `src/form_factor/cylinder/wrapper.py`:

```python
"""
Python wrapper for cylinder form factor C library.
"""

import os
import sys
import ctypes
import platform

def _load_library():
    """Load the compiled C library for the current platform."""
    lib_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Determine library extension
    if platform.system() == "Windows":
        lib_name = "cylinder.pyd"
    elif platform.system() == "Darwin":
        lib_name = "cylinder.so"
    else:
        lib_name = "cylinder.so"
    
    lib_path = os.path.join(lib_dir, lib_name)
    
    if not os.path.exists(lib_path):
        raise FileNotFoundError(
            f"Compiled library not found at {lib_path}. "
            f"Please run 'python setup.py build_py' first."
        )
    
    try:
        lib = ctypes.CDLL(lib_path)
    except OSError as e:
        raise OSError(f"Failed to load library {lib_path}: {e}")
    
    # Define function signatures
    lib.Iq.argtypes = [
        ctypes.c_double,  # q
        ctypes.c_double,  # sld
        ctypes.c_double,  # solvent_sld
        ctypes.c_double,  # radius
        ctypes.c_double   # length
    ]
    lib.Iq.restype = ctypes.c_double
    
    lib.form_volume.argtypes = [
        ctypes.c_double,  # radius
        ctypes.c_double   # length
    ]
    lib.form_volume.restype = ctypes.c_double
    
    return lib

# Load library on import
_lib = _load_library()

def compute_form_factor(q, sld, solvent_sld, radius, length, **kwargs):
    """
    Compute cylinder form factor squared.
    
    Parameters
    ----------
    q : float
        Scattering vector magnitude (Å⁻¹)
    sld : float
        Cylinder scattering length density (Å⁻²)
    solvent_sld : float
        Solvent scattering length density (Å⁻²)
    radius : float
        Cylinder radius (Å)
    length : float
        Cylinder length (Å)
    **kwargs : dict
        Additional ignored parameters for compatibility
    
    Returns
    -------
    float
        Form factor squared |F(q)|²
    """
    return _lib.Iq(q, sld, solvent_sld, radius, length)

def compute_volume(radius, length):
    """Compute cylinder volume."""
    return _lib.form_volume(radius, length)
```

Create `src/form_factor/cylinder/__init__.py`:

```python
"""Cylinder form factor model."""
from .wrapper import compute_form_factor, compute_volume
__all__ = ['compute_form_factor', 'compute_volume']
```

#### 4. Update Build System (`setup.py`)

The build system automatically detects new models, but you can verify by checking `setup.py`:

```python
# In setup.py, the FORM_FACTOR_MODELS list should include:
FORM_FACTOR_MODELS = [
    # ... existing models ...
    "cylinder",  # Your new model
]
```

Most likely, you don't need to modify `setup.py` as it auto-discovers models in `src/form_factor/`.

#### 5. Configure Model in `utils.py`

Edit `src/utils.py` to use your new model:

```python
# Line ~73: Change model configuration
FORM_FACTOR_MODEL = "cylinder"
STRUCTURE_FACTOR_MODEL = "hayter_msa"  # or "hardsphere" or None

# Lines ~213-240: Update parameter dictionaries
form_factor_for_fitting = np.vectorize(
    form_factor_2, 
    excluded=['scale', 'background', 'sld', 'solvent_sld', 'radius', 'length']
)

intensity_for_fitting = np.vectorize(
    intensity, 
    excluded=['scale', 'background', 'sld', 'solvent_sld', 'radius', 'length',
              'radius_effective', 'volfraction', 'charge', 'temperature', 
              'saltconc', 'dielectconst']
)

initial_params = {
    "scale": 1.0,
    "background": 0.001,
    "sld": 4.0e-6,
    "solvent_sld": 1.0e-6,
    "radius": 15.0,        # Cylinder radius
    "length": 50.0,        # Cylinder length
    # Structure factor parameters (if needed)
    "radius_effective": 20.0,
    "volfraction": 0.1,
    "charge": 25.0,
    "temperature": 300.0,
    "saltconc": 0.1,
    "dielectconst": 78.3
}

fit_params = {
    "scale": True,
    "background": True,
    "sld": True,
    "solvent_sld": False,
    "radius": True,
    "length": True,
    "radius_effective": True,
    "volfraction": True,
    "charge": True,
    "temperature": False,
    "saltconc": True,
    "dielectconst": False
}
```

#### 6. Build and Test

```bash
# Build the new model
python setup.py build_py

# Verify compilation
ls src/form_factor/cylinder/*.so     # Linux/macOS
dir src\form_factor\cylinder\*.pyd   # Windows

# Test the model
python -c "from src.form_factor.cylinder import wrapper; print('Cylinder model OK')"

# Run full test
python src/utils.py
```

### Key Design Principles

1. **Modular C Libraries**: Each model is a separate shared library (`.so`/`.pyd`/`.dll`)
2. **Shared Core Functions**: Use `libsas_core` for Bessel functions, quadrature, etc.
3. **Consistent Interfaces**: All wrappers expose `compute_form_factor(q, **kwargs)`
4. **Dictionary-Driven**: Parameters passed as `**kwargs` for maximum flexibility
5. **Auto-Discovery**: Build system finds and compiles all models automatically

### Adding a New Structure Factor

The process is identical, but place files in `src/structure_factor/<model_name>/`:

1. Create `model.c` with `Iq(q, radius_effective, volfraction, ...)` function
2. Create `wrapper.py` exposing `compute_structure_factor(q, **kwargs)`
3. Update `STRUCTURE_FACTOR_MODEL` in `utils.py`
4. Build with `python setup.py build_py`

### Testing Your Model

Create a simple test script:

```python
import sys
sys.path.insert(0, 'src')
from utils import form_factor, intensity
import numpy as np

# Test form factor
q_vals = np.logspace(-2, 0, 50)
params = {
    "sld": 4.0e-6,
    "solvent_sld": 1.0e-6,
    "radius": 15.0,
    "length": 50.0
}

for q in q_vals[:5]:
    F2 = form_factor(q, **params)
    print(f"q={q:.4f}: F²={F2:.6e}")

# Test full intensity with structure factor
full_params = {
    **params,
    "radius_effective": 20.0,
    "volfraction": 0.1,
    "charge": 25.0,
    "temperature": 300.0,
    "saltconc": 0.1,
    "dielectconst": 78.3
}

I_q = intensity(q_vals[0], scale=1.0, background=0.001, **full_params)
print(f"\nTotal intensity I(q): {I_q:.6e}")
```

### Resources

- **Example Models**: See existing implementations in `src/form_factor/sphere/`, `src/form_factor/ellipsoid/`, etc.
- **SasView Source**: https://github.com/SasView/sasmodels for reference implementations
- **Build System**: Review `setup.py` for compilation flags and RPATH configuration
- **Detailed Guide**: See `EXAMPLE_ADDING_NEW_MODEL.md` for more examples

### Common Pitfalls

1. **Missing Function Exports**: Ensure C functions are not `static` and have proper signatures
2. **Parameter Mismatches**: `wrapper.py` parameter names must match `utils.py` dictionaries
3. **Library Dependencies**: Structure factors may need `libsas_core` for numerical functions
4. **RPATH Issues (Linux)**: `setup.py` automatically configures RPATH; don't modify manually
5. **Windows DLL Loading**: Ensure `libsas_core.pyd` is in `PATH` or same directory

The framework will work seamlessly with your new model once these steps are complete—all fitting, bootstrapping, and plotting functions automatically adapt to the parameter dictionaries you provide!

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
