# Changelog

All notable changes to this project will be documented in this file.

## [0.3.0] - 2025-10-03

### Added
- **Cluster Computing Framework**: Complete ETH HPC (Euler/Leonhard) integration
  - `transfer.sh`: Comprehensive file transfer and job management script
  - `submit_job.sh`: SLURM job submission with automatic resource allocation
  - `setup_cluster.py`: Automated dependency installation on cluster
  - `process_data.py`: Optimized batch processing for HDF5 output only
- **Data Extraction Tools**: Modular functions for bootstrap result analysis
  - `data_extraction_functions.py`: Complete suite of analysis functions
  - `data_extraction_example.py`: Usage examples and workflows
  - `fitted_params_table.py`: Parameter validation and quality assurance
- **Improved Documentation**:
  - Standardized NumPy-style docstrings across all modules
  - Enhanced module headers with comprehensive usage examples
  - Added `cluster/README.md` with complete cluster workflow documentation
  - Improved function parameter descriptions and return value documentation

### Changed
- **Streamlined Project Structure**: Removed deprecated files and scripts
  - Removed `main.py`, `data.py` (functionality integrated into `utils.py`)
  - Removed `initial_params_all_structure_factors.json` (use single config)
  - Deprecated `collect_results.py` (replaced by `transfer.sh retrieve`)
  - Moved old code to `src/old/` directory for reference
- **Enhanced Transfer Script**: Made `retrieve` the primary download method
  - Intelligent file exclusions (old/, *.h5, *.so, .git/)
  - Comprehensive command documentation in header
  - Added 11 commands: to, retrieve, from, test, status, check, logs, viewlog, clean, list, delete
- **Improved Documentation Format**: Consistent ReStructuredText-style formatting
  - All module docstrings follow scientific Python standards
  - Better IDE integration and Sphinx compatibility
  - Clear section headers and hierarchical organization

### Fixed
- Documentation consistency across all Python modules
- Cluster workflow commands and file transfer logic
- Parameter dictionary handling in custom model examples

## [0.2.0] - 2025-09-29

### Added
- Block bootstrapping functionality for time-series analysis
- Hayter-Penfold MSA structure factor calculations
- Advanced parameter fitting with uncertainty estimation
- Comprehensive visualization and plotting tools
- C extensions for high-performance form factor calculations

### Changed
- Reorganized project structure with proper package layout
- Updated documentation to emphasize utils.py as main interface
- Improved installation process for cross-platform compatibility

### Fixed
- Build system compatibility issues
- Memory management in C extensions

## [0.1.0] - Initial Release

### Added
- Basic form factor calculations for core-shell cylinders
- Python wrappers for C implementations
- Initial bootstrapping framework
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
