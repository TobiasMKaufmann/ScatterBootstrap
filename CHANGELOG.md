# Changelog

All notable changes to this project will be documented in this file.

## [0.4.0] - 2026-06-12

### Added
- **Parallel bootstrap.** `residuals_bootstrap` now takes an `n_jobs` argument
  (`1` serial, `-1` all cores, `N` for N processes) that runs the independent
  refits across worker processes for a near-linear speedup. Results are
  deterministic and identical to a serial run for the same `rng` seed,
  regardless of `n_jobs`, and the HDF5-store output path is preserved. The
  cluster pipeline (`process_data.py`) now sets `n_jobs` from
  `$SLURM_CPUS_PER_TASK`, so allocating more cores actually speeds it up.
- **Batch API `fit_bootstrap_many()`.** Runs the full fit -> bootstrap ->
  confidence-interval pipeline over a collection of datasets and parallelizes
  across them, with automatic core budgeting (no oversubscription/nesting) and
  per-dataset configuration support. Reproducible and independent of `n_jobs`.
- Automated `pytest` test suite (`tests/`) covering the public API, every
  bundled C-extension model, fitting, bootstrapping, and confidence intervals.
- Continuous integration (`.github/workflows/ci.yml`): builds the C extensions
  and runs the tests on Linux/macOS/Windows across Python 3.9–3.12, plus lint
  (`black`, `flake8`) and a JOSS paper-draft build.
- JOSS submission materials: `paper/paper.md` and `paper/paper.bib`.
- Community/contribution docs: `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`,
  `CITATION.cff`, and a `.flake8` configuration.
- The build system now **auto-discovers** models (any `<name>/<name>.c` under
  `form_factors/` or `structure_factors/`) and auto-generates `package_data`.
- **Parallel compilation** of the model extensions (one thread per CPU core,
  after `libsas_core` is built). Override with `SCATTERBOOTSTRAP_BUILD_JOBS=N`
  (or `MAX_JOBS`); set to `1` for a serial build.

### Changed
- Renamed the installable package to `scatterbootstrap` with a clean, name-based
  public API (`form_factor`, `structure_factor`, `intensity`, `fit_data`,
  `residuals_bootstrap`, ...). Models are selected by name at call time.
- Renamed the model sub-packages to `form_factors` and `structure_factors`
  (plural) — see the fix below.
- Rewrote `EXAMPLE_ADDING_NEW_MODEL.md` and the README to match the current
  architecture; corrected the model parameter tables.
- The Docker image now builds and installs the package (compiling all C
  extensions) and verifies the import.

### Fixed
- **Critical:** the public `form_factor`/`structure_factor` functions were
  shadowed by the same-named sub-packages once model discovery imported them,
  which broke the entire public API. Renaming the sub-packages to plural form
  resolves the collision (regression-tested).
- `requirements.txt` no longer lists unused packages (seaborn, plotly, pyvista,
  pydantic, jupyter, ...) and now mirrors the real runtime dependencies.
- Removed stale build artifacts and corrected `.gitignore`/`MANIFEST.in`.

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
