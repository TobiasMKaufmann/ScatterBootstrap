# ScatterBootstrap: Advanced Small-Angle Scattering Analysis

[![CI](https://github.com/TobiasMKaufmann/ScatterBootstrap/actions/workflows/ci.yml/badge.svg)](https://github.com/TobiasMKaufmann/ScatterBootstrap/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.8+](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/)

A comprehensive Python package for analyzing small-angle scattering (SAS) data with **14 form factor models** and **2 structure factor models**, featuring residual-bootstrap uncertainty quantification and high-performance cross-platform C extensions. The scattering model kernels are adapted from [SasView](https://www.sasview.org/) (BSD-3-Clause).

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
git clone https://github.com/TobiasMKaufmann/ScatterBootstrap.git
cd ScatterBootstrap
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

### 4. Build and Install the Package

The build system automatically detects your platform and compiler, compiles all 16
C extensions (`libsas_core` plus 14 form factor and 2 structure factor models), and
installs `scatterbootstrap` in editable mode:

```bash
pip install --upgrade pip
pip install -e .[dev]
```

**What Gets Built:**
- `libsas_core` - Shared library with Bessel functions, quadrature, and utilities
- **Form Factors**: sphere, ellipsoid, barbell, core_shell_cylinder, core_multi_shell, elliptical_cylinder, fuzzy_sphere, lamellar_hg, linear_pearls, onion, polymer_micelle, pringle, bcc_paracrystal, fcc_paracrystal
- **Structure Factors**: hayter_msa, hardsphere

**Build System Features:**
- Automatic MSVC detection and configuration on Windows
- Proper RPATH settings on Linux/macOS for library dependencies
- Intelligent function export detection
- Automatic discovery of new models (no `setup.py` edits required)
- **Parallel compilation** of the model extensions (one job per CPU core;
  override with `SCATTERBOOTSTRAP_BUILD_JOBS=N`, or `=1` to build serially)

You can verify the build directly:
```bash
ls src/scatterbootstrap/lib/*.so src/scatterbootstrap/form_factors/*/*.so src/scatterbootstrap/structure_factors/*/*.so   # Linux/macOS
dir src\scatterbootstrap\lib\*.pyd src\scatterbootstrap\form_factors\*\*.pyd src\scatterbootstrap\structure_factors\*\*.pyd  # Windows
```

### 5. Verify Installation

```bash
python -m scatterbootstrap.core
```

This runs a small built-in demo (fits a noisy sphere form factor) and prints the
recovered parameters, confirming the package and all C extensions loaded correctly.

## Available Models

### Form Factors (14 Models)

The package includes comprehensive form factor implementations for various particle geometries:

| Model | Description | Key Parameters |
|-------|-------------|----------------|
| **sphere** | Homogeneous sphere | `sld`, `sld_solvent`, `radius` |
| **ellipsoid** | Prolate/oblate ellipsoid | `sld`, `sld_solvent`, `radius_polar`, `radius_equatorial` |
| **core_shell_cylinder** | Cylinder with shell coating | `core_sld`, `shell_sld`, `solvent_sld`, `radius`, `thickness`, `length` |
| **barbell** | Dumbbell-shaped particles | `sld`, `solvent_sld`, `radius_bell`, `radius`, `length` |
| **core_multi_shell** | Multi-layer spherical shells | `core_sld`, `core_radius`, `solvent_sld`, `n_shells`, `sld_array[N]`, `thickness_array[N]` |
| **elliptical_cylinder** | Cylinder with elliptical cross-section | `radius_minor`, `r_ratio`, `length`, `sld`, `solvent_sld` |
| **fuzzy_sphere** | Sphere with fuzzy interface | `sld`, `sld_solvent`, `radius`, `fuzziness` |
| **lamellar_hg** | Head-group bilayer | `length_tail`, `length_head`, `sld`, `sld_head`, `sld_solvent` |
| **linear_pearls** | Linear chain of spheres | `radius`, `edge_sep`, `fp_num_pearls`, `pearl_sld`, `solvent_sld` |
| **onion** | Multi-shell sphere (onion model) | `sld_core`, `radius_core`, `sld_solvent`, `n_shells`, `sld_in[N]`, `sld_out[N]`, `thickness[N]`, `A[N]` |
| **polymer_micelle** | Star polymer micelle | `ndensity`, `v_core`, `v_corona`, `solvent_sld`, `core_sld`, `corona_sld`, `radius_core`, `rg`, `d_penetration`, `n_aggreg` |
| **pringle** | Hyperbolic paraboloid | `radius`, `thickness`, `alpha`, `beta`, `sld`, `sld_solvent` |
| **bcc_paracrystal** | Body-centered cubic lattice | `dnn`, `d_factor`, `radius`, `sld`, `solvent_sld` |
| **fcc_paracrystal** | Face-centered cubic lattice | `dnn`, `d_factor`, `radius`, `sld`, `solvent_sld` |

### Structure Factors (2 Models)

Interparticle interference effects for concentrated systems:

| Model | Description | Key Parameters |
|-------|-------------|----------------|
| **hayter_msa** | Hayter-Penfold MSA for charged particles | `radius_effective`, `volfraction`, `charge`, `temperature`, `saltconc`, `dielectconst` |
| **hardsphere** | Hard sphere repulsion | `radius_effective`, `volfraction` |

### Model Architecture

All models follow a modular design:
- **C Implementation**: High-performance kernel in `src/scatterbootstrap/form_factors/<model>/<model>.c`
- **Python Wrapper**: Easy-to-use interface in `src/scatterbootstrap/form_factors/<model>/wrapper.py`
- **Shared Core**: Common functions (Bessel, quadrature) in `src/scatterbootstrap/lib/libsas_core`
- **Explicit Selection**: Models are selected by name, passed as `form_factor_model="..."` /
  `structure_factor_model="..."` to `form_factor()`, `structure_factor()`, `intensity()`,
  `fit_data()`, etc. Use `scatterbootstrap.list_form_factor_models()` and
  `scatterbootstrap.list_structure_factor_models()` to see all available names.

**Adding New Models**: See the "Implementing Custom Models" section below for a complete guide.

## Quick Start

### Basic Usage Example

Models are selected by **name**, passed directly as arguments to `form_factor()`,
`structure_factor()`, and `intensity()` — no source code edits required.

```python
from scatterbootstrap import form_factor, structure_factor, intensity
import numpy as np

# Define scattering parameters as keyword arguments
q = 0.1  # scattering vector (Å⁻¹)

# Barbell form factor parameters
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
F2 = form_factor(q, "barbell", **model_params)

# Calculate structure factor
S_q = structure_factor(q, "hayter_msa", **structure_params)

# Total scattering intensity with scaling
scale = 1.0
background = 0.001
I_q = intensity(q, scale, background, "barbell", "hayter_msa", **model_params, **structure_params)

print(f"Form Factor F²(q): {F2:.6e}")
print(f"Structure Factor S(q): {S_q:.4f}")
print(f"Total Intensity I(q): {I_q:.6e}")
```

**Switching Models**: To use a different form factor (e.g., `sphere`, `core_shell_cylinder`,
`ellipsoid`) or structure factor (`hardsphere`), simply pass a different model name and the
matching parameters:

```python
from scatterbootstrap import form_factor, list_form_factor_models, list_structure_factor_models

print(list_form_factor_models())       # all 14 available form factor model names
print(list_structure_factor_models())  # all 2 available structure factor model names

F2 = form_factor(q, "sphere", sld=4.0e-6, sld_solvent=1.0e-6, radius=50.0)
```

Each model's required parameters are documented in its wrapper module, e.g.
`scatterbootstrap.form_factors.sphere.wrapper.compute_form_factor`.

### Data Analysis Workflow

The framework provides a complete pipeline for fitting experimental data and quantifying uncertainties through bootstrap resampling.

```python
from scatterbootstrap import fit_data, residuals_bootstrap, compute_confidence_intervals, plot_fit_data
import numpy as np

# Choose the form factor and (optional) structure factor models by name
FORM_FACTOR_MODEL = "barbell"
STRUCTURE_FACTOR_MODEL = "hayter_msa"  # set to None to fit form factor only

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
    form_factor_model=FORM_FACTOR_MODEL,
    structure_factor_model=STRUCTURE_FACTOR_MODEL,
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
    form_factor_model=FORM_FACTOR_MODEL,
    structure_factor_model=STRUCTURE_FACTOR_MODEL,
    all_params=fitted_dict,      # Use fitted values as starting point
    fit_params=fit_params,
    n_iterations=1000,           # Increase for better statistics
    rng=42,                      # Optional seed for reproducibility
    n_jobs=-1,                   # Use all CPU cores (1 = serial, N = N processes)
)

# Step 3: Compute confidence intervals
confidence_intervals = compute_confidence_intervals(bootstrap_results, confidence_level=0.95)

print("\n95% Confidence Intervals:")
for param, (lower, upper) in confidence_intervals.items():
    mean_val = np.mean([r[param] for r in bootstrap_results])
    print(f"  {param}: {mean_val:.6e} [{lower:.6e}, {upper:.6e}]")

# Step 4: Visualize results
print("\nGenerating plots...")
plot_fit_data(
    q_exp, I_exp,
    params=fitted_dict,
    form_factor_model=FORM_FACTOR_MODEL,
    structure_factor_model=STRUCTURE_FACTOR_MODEL,
    title="Barbell Model Fit",
    folder="./results",          # Output directory
)

print("Analysis complete! Results saved to ./results/")
```

**Key Functions:**

- **`fit_data()`**: Non-linear least squares fitting using scipy's Levenberg-Marquardt algorithm
- **`residuals_bootstrap()`**: Resamples residuals to quantify parameter uncertainties (parallel via `n_jobs`)
- **`fit_bootstrap_many()`**: Fits + bootstraps a whole collection of datasets in parallel
- **`compute_confidence_intervals()`**: Calculates percentile-based confidence intervals
- **`plot_fit_data()`**: Creates publication-ready plots with fit overlays

### Batch Processing Many Datasets

`fit_bootstrap_many()` runs the full **fit → bootstrap → confidence interval**
pipeline for many datasets and parallelizes the work across CPU cores. It
budgets cores automatically (parallelizing across datasets, or — for a single
dataset — across that dataset's bootstrap) so it never oversubscribes, and it is
reproducible: a given `rng` seed yields the same result regardless of `n_jobs`.

```python
import numpy as np
import scatterbootstrap as sb

# name -> (q, I) for each measurement
datasets = {
    "sample_A": (q_A, I_A),
    "sample_B": (q_B, I_B),
    "sample_C": (q_C, I_C),
}

initial_params = {"scale": 1.0, "background": 0.001,
                  "sld": 4e-6, "sld_solvent": 1e-6, "radius": 50.0}
fit_params = {"scale": True, "background": True, "sld": False,
              "sld_solvent": False, "radius": True}

results = sb.fit_bootstrap_many(
    datasets,
    form_factor_model="sphere",
    initial_params=initial_params,   # or a {name: params} mapping per dataset
    fit_params=fit_params,
    n_iterations=1000,
    rng=42,
    n_jobs=-1,                       # use all cores across datasets
)

for name, res in results.items():
    lo, hi = res["confidence_intervals"]["radius"]
    print(f"{name}: radius = {res['fitted_params']['radius']:.2f}  95% CI [{lo:.2f}, {hi:.2f}]")
```

Each `results[name]` is a dict with `fitted_params`, `param_order`,
`covariance`, `confidence_intervals`, and (unless `keep_ensembles=False`) the
full `bootstrap` ensemble. Pass `initial_params`/`fit_params`/`bounds` either as
a single shared config or as a `{name: ...}` mapping for per-dataset settings.

> **macOS/Windows:** call `fit_bootstrap_many` (and `residuals_bootstrap` with
> `n_jobs != 1`) from inside an `if __name__ == "__main__":` guard, as required
> by Python's `multiprocessing`. On Linux this is not needed.

**Performance Tips:**

- Start with `n_iterations=100` for testing, increase to 1000-5000 for final analysis
- **Parallelize the bootstrap** with `n_jobs`: the refits are independent, so
  `n_jobs=-1` (all cores) gives a near-linear speedup. Results are identical to a
  serial run for the same `rng` seed, regardless of `n_jobs`.
- Use the cluster computing framework (`src/cluster/`) for large bootstrap analyses
  (it automatically sets `n_jobs` from `$SLURM_CPUS_PER_TASK`)
- Set `structure_factor_model=None` if structure factor effects are negligible

## Project Structure

```
ScatterBootstrap/
├── src/
│   ├── scatterbootstrap/                  # The installable Python package
│   │   ├── __init__.py                    # Public API (START HERE)
│   │   ├── core.py                        # Main analysis functions
│   │   ├── _lib_finder.py                 # Locates compiled .so/.pyd/.dll files
│   │   │
│   │   ├── lib/                           # Shared C library components
│   │   │   ├── libsas_core.so/.pyd/.dll   # Compiled shared library
│   │   │   ├── sas_J1.c/h                 # Bessel J1 functions
│   │   │   ├── sas_J0.c/h                 # Bessel J0 functions
│   │   │   ├── sas_JN.c/h                 # Bessel Jn functions
│   │   │   ├── sas_3j1x_x.c               # 3*j1(x)/x function
│   │   │   ├── gauss76.c/h                # 76-point Gauss quadrature
│   │   │   ├── gauss150.c/h               # 150-point Gauss quadrature
│   │   │   ├── polevl.c/h                 # Polynomial evaluation
│   │   │   ├── utils.c/h                  # Math utilities (SINCOS, etc.)
│   │   │   └── sas_core.h                 # Common header and constants
│   │   │
│   │   ├── form_factors/                   # Form factor models (14 models)
│   │   │   ├── __init__.py
│   │   │   ├── sphere/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── wrapper.py             # Python interface
│   │   │   │   ├── sphere.c               # C implementation
│   │   │   │   └── sphere.so/.pyd/.dll    # Compiled library
│   │   │   ├── ellipsoid/                 # [Same structure]
│   │   │   ├── core_shell_cylinder/       # [Same structure]
│   │   │   ├── barbell/                   # [Same structure]
│   │   │   ├── core_multi_shell/          # [Same structure]
│   │   │   ├── elliptical_cylinder/       # [Same structure]
│   │   │   ├── fuzzy_sphere/              # [Same structure]
│   │   │   ├── lamellar_hg/               # [Same structure]
│   │   │   ├── linear_pearls/             # [Same structure]
│   │   │   ├── onion/                     # [Same structure]
│   │   │   ├── polymer_micelle/           # [Same structure]
│   │   │   ├── pringle/                   # [Same structure]
│   │   │   ├── bcc_paracrystal/           # [Same structure + sphere_form.c]
│   │   │   └── fcc_paracrystal/           # [Same structure + sphere_form.c]
│   │   │
│   │   └── structure_factors/              # Structure factor models (2 models)
│   │       ├── __init__.py
│   │       ├── hayter_msa/
│   │       │   ├── __init__.py
│   │       │   ├── wrapper.py             # Python interface
│   │       │   ├── hayter_msa.c           # C implementation
│   │       │   └── hayter_msa.so/.pyd/.dll # Compiled library
│   │       └── hardsphere/                # [Same structure]
│   │
│   ├── data_extraction_functions.py       # Bootstrap results analysis tools
│   ├── data_extraction_example.py         # Usage examples for data extraction
│   ├── fitted_params_table.py             # Parameter validation utilities
│   ├── plot_comparisons.py                # Visualization and comparison tools
│   ├── initial_params.json                # Default parameter configurations
│   │
│   └── cluster/                           # ETH HPC cluster computing framework
│       ├── README.md                      # Complete cluster workflow guide
│       ├── process_data.py                # Batch bootstrap processing
│       ├── submit_job.sh                  # SLURM job submission script
│       ├── setup_cluster.py               # Dependency installation for cluster
│       ├── transfer.sh                    # File transfer and job management
│       └── requirements_cluster.txt       # Minimal cluster dependencies
│
├── tests/                                  # pytest test suite
│
├── requirements.txt                       # Python dependencies
├── setup.py                               # Cross-platform build system with MSVC support
├── pyproject.toml                         # Modern Python package configuration
├── MANIFEST.in                            # Package manifest for distribution
├── LICENSE                                # MIT License
├── CHANGELOG.md                           # Version history and changes
├── EXAMPLE_ADDING_NEW_MODEL.md           # Guide for adding new models
└── README.md                              # This file
```

**Key Directories:**
- **`src/scatterbootstrap/lib/`**: Shared C library used by all models
- **`src/scatterbootstrap/form_factors/`**: Individual form factor implementations (each in its own subdirectory)
- **`src/scatterbootstrap/structure_factors/`**: Structure factor implementations
- **`src/cluster/`**: HPC cluster tools for large-scale analysis
- **`tests/`**: Automated test suite (run with `pytest`)

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
- Verify `libsas_core.lib` and `libsas_core.pyd` exist in `src/scatterbootstrap/lib/`
- Rebuild: `python setup.py clean --all && pip install -e .`

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
- Verify C extensions built: `ls src/scatterbootstrap/form_factors/sphere/*.so` (Linux/macOS) or `dir src\scatterbootstrap\form_factors\sphere\*.pyd` (Windows)
- Rebuild: `pip install -e .`
- Check for compilation errors in build output

#### 7. Windows: UNC Path Errors
```
CMD.exe does not support UNC paths as current directories
```
**Solution**: Map network drive to a letter (e.g., `Z:\`) or work from local directory.

### Build System Diagnostics

**Check Build Status:**
```bash
# Verify the package imports and lists all compiled models
python -c "import scatterbootstrap as sb; print(sb.list_form_factor_models()); print(sb.list_structure_factor_models())"

# List built libraries
ls src/scatterbootstrap/lib/*.so src/scatterbootstrap/form_factors/*/*.so src/scatterbootstrap/structure_factors/*/*.so     # Linux/macOS
dir src\scatterbootstrap\lib\*.pyd src\scatterbootstrap\form_factors\*\*.pyd src\scatterbootstrap\structure_factors\*\*.pyd # Windows
```

**Clean and Rebuild:**
```bash
# Remove compiled artifacts, then rebuild from scratch
python setup.py clean --all
pip install -e .
```

### Performance Notes

- C extensions provide 50-100x speedup over pure Python implementations
- For large datasets, consider using the cluster processing scripts in `src/cluster/`
- Bootstrap analysis can be computationally intensive; start with smaller sample sizes for testing

## Testing

The package ships with an automated `pytest` suite that builds and exercises
every compiled model plus the fitting and bootstrap pipeline:

```bash
pip install -e .[dev]
pytest                              # run all tests
pytest --cov=scatterbootstrap       # with a coverage report
```

## Development and Contributing

Contributions are welcome — see [CONTRIBUTING.md](CONTRIBUTING.md) for the full
guide and [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) for community expectations.
Bug reports and questions go to the
[issue tracker](https://github.com/TobiasMKaufmann/ScatterBootstrap/issues).

```bash
# Format and lint before opening a pull request
black src/scatterbootstrap tests
flake8 src/scatterbootstrap tests --max-line-length=100 --extend-ignore=E203,W503
```

## Implementing Custom Models

Models are **auto-discovered and auto-compiled**: dropping a new model directory
into the package is all that is required — no edits to `setup.py` or `core.py`.

### Add a form factor in four steps

1. **Create the directory** `src/scatterbootstrap/form_factors/<name>/`
   (use `structure_factors/` for a structure factor) containing:
   - `<name>.c` and `<name>.h` — the C kernel,
   - `wrapper.py` — the thin Python interface,
   - `__init__.py`.

2. **Write the C kernel.** Form factor kernels expose an `Fq(...)` function and
   may reuse the shared numerical core (`#include "../../lib/sas_core.h"` for
   Bessel functions, Gauss–Legendre quadrature, etc.). Structure factor kernels
   expose an `Iq(...)` function. Keep the exported functions non-`static`.

   ```c
   /* sphere.c — adapted from SasView (https://www.sasview.org/) */
   #include "../../lib/sas_core.h"

   void Fq(double q, double *f1, double *f2,
           double sld, double sld_solvent, double radius) {
       const double bes = sas_3j1x_x(q * radius);
       const double contrast = sld - sld_solvent;
       const double volume = M_4PI_3 * radius * radius * radius;
       const double fq = contrast * volume * bes;
       *f1 = 1.0e-2 * fq;            /* <F>   */
       *f2 = 1.0e-4 * fq * fq;       /* <F^2> */
   }
   ```

3. **Write `wrapper.py`** exposing `compute_form_factor(q, **params)` (or
   `compute_structure_factor`). Use `find_library` to locate the compiled binary
   in a platform-independent way:

   ```python
   import ctypes, os
   import numpy as np
   from ..._lib_finder import find_library

   _lib = ctypes.CDLL(find_library("sphere", os.path.dirname(__file__)))
   _lib.Fq.restype = None
   _lib.Fq.argtypes = [ctypes.c_double, ctypes.POINTER(ctypes.c_double),
                       ctypes.POINTER(ctypes.c_double),
                       ctypes.c_double, ctypes.c_double, ctypes.c_double]

   def compute_form_factor(q, sld, sld_solvent, radius, **kwargs):
       q = np.atleast_1d(q).astype(float)
       out = np.zeros_like(q)
       f1, f2 = ctypes.c_double(), ctypes.c_double()
       for i, qv in enumerate(q):
           _lib.Fq(qv, ctypes.byref(f1), ctypes.byref(f2), sld, sld_solvent, radius)
           out[i] = f2.value
       return out
   ```

   `__init__.py`:

   ```python
   from .wrapper import compute_form_factor
   __all__ = ["compute_form_factor"]
   ```

4. **Rebuild and test.** `pip install -e .` compiles the new kernel, and the
   model is immediately available by name:

   ```python
   import scatterbootstrap as sb
   print(sb.list_form_factor_models())          # your model now appears
   sb.form_factor(0.1, "<name>", sld=4e-6, sld_solvent=1e-6, radius=50)
   ```

   Add a representative parameter set to `tests/conftest.py` so the smoke tests
   cover your model, then run `pytest`.

### Design principles

1. **Modular C libraries** — each model is a separate shared library.
2. **Shared core** — reuse `libsas_core` for Bessel functions and quadrature.
3. **Uniform interface** — every wrapper exposes a `compute_*` function taking
   `q` and `**params`.
4. **Name-based selection** — models are chosen at call time, never by editing
   source.
5. **Auto-discovery** — the build system finds and compiles all models.

See [EXAMPLE_ADDING_NEW_MODEL.md](EXAMPLE_ADDING_NEW_MODEL.md) for a fuller
walkthrough and the existing `sphere`/`hardsphere` models for reference.

## License

MIT License - see [LICENSE](LICENSE) file for details.

**Note**: The scattering model kernels in `src/scatterbootstrap/form_factors/` and
`src/scatterbootstrap/structure_factors/`, and the shared numerical core in
`src/scatterbootstrap/lib/`, are adapted from [SasView](https://www.sasview.org/)
and are subject to SasView's BSD 3-Clause License. All C source files contain
appropriate attribution headers.

## Citation

If you use this software in your research, please cite it using the metadata in
[CITATION.cff](CITATION.cff), or:

```bibtex
@software{scatterbootstrap,
  title   = {ScatterBootstrap: Small-angle scattering model fitting with
             bootstrap-based uncertainty quantification},
  author  = {Kaufmann, Tobias},
  year    = {2025},
  url     = {https://github.com/TobiasMKaufmann/ScatterBootstrap},
  version = {0.4.0}
}
```

## Contact

- **Author**: Tobias Kaufmann
- **Email**: tkaufman@student.ethz.ch
- **Repository**: https://github.com/TobiasMKaufmann/ScatterBootstrap

---

**Note**: This package is designed for scientific research in small-angle scattering
analysis. The main analysis API lives in `scatterbootstrap.core` (re-exported from
the top-level `scatterbootstrap` package) and provides tools for computing
scattering intensities, fitting, bootstrapping, and uncertainty analysis.
