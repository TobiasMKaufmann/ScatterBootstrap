# Release Notes - Version 0.3.0

**Release Date:** October 3, 2025

## Overview

Version 0.3.0 represents a major enhancement to the ECHEMES Bootstrapping framework, focusing on **cluster computing integration**, **comprehensive documentation improvements**, and **streamlined project structure**. This release makes the package production-ready for high-throughput bootstrap analysis on HPC systems while maintaining ease of use for local analysis.

## 🚀 Major Features

### 1. Complete Cluster Computing Framework

A full-featured cluster computing infrastructure for ETH HPC (Euler/Leonhard) systems:

**New Files:**
- `src/cluster/transfer.sh` - Comprehensive file transfer and job management (11 commands)
- `src/cluster/submit_job.sh` - SLURM job submission with automatic resource allocation
- `src/cluster/setup_cluster.py` - Automated dependency installation on cluster
- `src/cluster/process_data.py` - Optimized batch processing with HDF5-only output
- `src/cluster/requirements_cluster.txt` - Minimal dependencies for cluster environment
- `src/cluster/README.md` - Complete cluster workflow documentation

**Key Capabilities:**
- Single-command workflow: upload, build, submit, monitor, download
- Intelligent file exclusions (old/, *.h5, *.so, .git/, __pycache__/)
- Remote job monitoring with comprehensive status checks
- Log file viewing and management
- Automatic HDF5 result collection and archiving
- Support for 5000+ bootstrap iterations per dataset

**Available Commands:**
```bash
./transfer.sh to        # Upload and submit job
./transfer.sh retrieve  # Download results (PRIMARY)
./transfer.sh status    # Check SLURM queue
./transfer.sh check     # Comprehensive status
./transfer.sh logs      # List log files
./transfer.sh viewlog   # View specific log
./transfer.sh clean     # Remove temp files
./transfer.sh list      # List cluster files
./transfer.sh delete    # Remove all files
./transfer.sh test      # Test environment
```

### 2. Data Extraction and Analysis Tools

Complete suite of modular functions for bootstrap result analysis:

**New Files:**
- `src/data_extraction_functions.py` - 9 analysis functions
- `src/data_extraction_example.py` - Comprehensive usage examples
- `src/fitted_params_table.py` - Parameter validation utilities

**Functions:**
- `load_confidence_intervals()` - Load results from HDF5 files
- `identify_varying_parameters()` - Find non-fixed parameters
- `plot_confidence_intervals_comparison()` - Multi-dataset comparison plots
- `plot_confidence_intervals_grid()` - Grid layout visualization
- `create_individual_parameter_plots()` - Per-parameter detailed plots
- `load_fitted_parameters()` - Extract bootstrap samples
- `plot_fitted_parameters_distributions()` - Distribution histograms
- `create_summary_dataframe()` - Statistical summary tables
- `process_bootstrap_data()` - Complete analysis pipeline

### 3. Enhanced Documentation

**Standardized Docstrings:**
All Python modules now use NumPy-style documentation:
- Clear Parameter/Returns sections with type annotations
- Comprehensive function descriptions
- Usage examples in docstrings
- Better IDE integration and Sphinx compatibility

**Updated Files:**
- `src/utils.py` - 9 functions standardized
- `src/data_extraction_functions.py` - 9 functions standardized
- `src/fitted_params_table.py` - 3 functions standardized
- `src/plot_comparisons.py` - 3 functions standardized
- `src/cluster/process_data.py` - Enhanced module header

**Improved Module Headers:**
- ReStructuredText-style formatting
- Clear section organization
- Code examples with syntax highlighting
- Feature descriptions and use cases
- Author and project attribution

## 🔄 Changes and Improvements

### Project Structure Cleanup

**Removed/Deprecated:**
- `src/main.py` - Functionality integrated into utils.py
- `src/data.py` - Functions moved to utils.py
- `src/initial_params_all_structure_factors.json` - Use single config file
- `src/cluster/collect_results.py` - Replaced by `transfer.sh retrieve`
- `src/cluster/test_c_extensions.py` - Not needed in automated workflow

**Reorganized:**
- Old code moved to `src/old/` directory for reference
- Cluster scripts consolidated in `src/cluster/`
- Clear separation between local and cluster workflows

### Enhanced Transfer Script

**Primary Download Method:**
- Made `retrieve` the recommended download command
- Deprecated `from` command (still functional)
- Added comprehensive header documentation

**Improved File Management:**
- Automatic exclusion patterns for unnecessary files
- Intelligent file size reduction for transfers
- Clean separation of old data (old/ excluded)
- Proper .gitignore integration

### README Updates

**Added:**
- Cluster Computing section with quick start guide
- Updated project structure reflecting current state
- Link to cluster/README.md for detailed workflow
- Improved quick start examples

**Updated:**
- Installation instructions for cluster compatibility
- Project structure tree (removed deprecated files)
- Key features highlighting cluster capabilities

## 📊 HDF5 Output Structure

Comprehensive data storage in each processed dataset:

```
dataset_name.h5
├── raw_data                    # Original q, I data
├── initial_params              # Starting values
├── residuals                   # Initial fit residuals
├── first_fit_params            # Initial fit results (value, fitted)
├── fitted_params/
│   ├── s0                      # Bootstrap sample 0 parameters
│   ├── s1                      # Bootstrap sample 1 parameters
│   └── ...                     # Up to s4999 (5000 samples)
├── synthetic_y/
│   ├── s0                      # Bootstrap sample 0 intensity
│   ├── s1                      # Bootstrap sample 1 intensity
│   └── ...                     # Up to s4999 (5000 samples)
├── confidence_intervals        # 95% CI by default
└── metadata
    ├── sample                  # Dataset name
    └── processing_stage        # "bootstrap_analysis"
```

## 🔧 Technical Improvements

### Cluster Compatibility
- Tested on ETH Euler and Leonhard Open clusters
- SLURM job scheduler integration
- Module system compatibility
- Fallback to system Python when modules unavailable
- Automatic C extension recompilation for cluster architecture

### Performance Notes
- Current implementation: Sequential processing (functional)
- Planned optimizations: Parallel processing, GPU acceleration
- Typical runtime: 4-8 hours for 5000 bootstrap iterations
- Memory efficient: 2GB per CPU core recommended

### Documentation Standards
- NumPy/SciPy style docstrings throughout
- Scientific Python community best practices
- IDE autocomplete and tooltip support
- Sphinx-ready for automated documentation generation

## 📦 Version Updates

**Updated Files:**
- `setup.py` - Version 0.3.0, enhanced description, added tqdm
- `pyproject.toml` - Version 0.3.0, Beta status, Python 3.12 support
- `CHANGELOG.md` - Complete changelog with all v0.3.0 changes
- `README.md` - Cluster section, updated structure, citation

**Development Status:**
- Upgraded from "Alpha" to "Beta"
- Production-ready for scientific research
- Stable API for core functions

## 🎯 Use Cases

### Local Analysis
```python
from src.utils import fit_data, residuals_bootstrap
from src.data_extraction_functions import process_bootstrap_data

# Run analysis locally (smaller datasets)
fitted_params, cov = fit_data(q_data, I_data, initial_params, fit_params)
bootstrap_results = residuals_bootstrap(q_data, I_data, fitted_params, 
                                       n_iterations=1000)

# Extract and visualize results
results = process_bootstrap_data('bootstrap_data', create_plots=True)
```

### Cluster Analysis
```bash
# High-throughput analysis (large datasets, 5000+ iterations)
cd src/cluster
./transfer.sh to        # Submit job
./transfer.sh check     # Monitor progress
./transfer.sh retrieve  # Download results
```

### Post-Processing
```python
from src.data_extraction_functions import (
    load_confidence_intervals,
    create_summary_dataframe,
    plot_confidence_intervals_grid
)

# Load cluster results
confidence_data = load_confidence_intervals('cluster/bootstrap_data')

# Generate comprehensive reports
summary_df = create_summary_dataframe('cluster/bootstrap_data',
                                     save_path='summary.csv')

# Create publication figures
plot_confidence_intervals_grid(confidence_data, varying_params,
                              save_path='figures/confidence_intervals.png')
```

## 🐛 Bug Fixes

- Fixed documentation consistency across all modules
- Corrected cluster workflow commands in transfer.sh
- Improved parameter dictionary handling in custom models
- Enhanced error handling in cluster scripts

## 🔜 Future Plans

### Performance Optimizations (v0.4.0)
- Parallel processing of multiple datasets
- Vectorized bootstrap iterations
- GPU acceleration support
- MPI distributed computing
- Memory-efficient data streaming

### Additional Features
- More scattering models (spheres, ellipsoids, etc.)
- Interactive visualization dashboard
- Automatic optimal parameter initialization
- Advanced statistical analysis tools

## 📚 Documentation

**Primary Documentation:**
- README.md - Main installation and usage guide
- src/cluster/README.md - Complete cluster workflow
- CHANGELOG.md - Detailed version history
- RELEASE_NOTES_v0.3.0.md - This file

**Code Documentation:**
- NumPy-style docstrings in all modules
- Inline comments for complex algorithms
- Usage examples in function docstrings

## 🙏 Acknowledgments

- **SasView Project** - Core scattering model implementations
- **ETH HPC Team** - Cluster access and support
- **Scientific Python Community** - Documentation standards

## 📧 Support

- **Issues**: https://github.com/TobiasMKaufmann/echemes-bootstrapping/issues
- **Email**: tkaufman@student.ethz.ch
- **Repository**: https://github.com/TobiasMKaufmann/echemes-bootstrapping

---

**Full Changelog**: https://github.com/TobiasMKaufmann/echemes-bootstrapping/blob/main/CHANGELOG.md
