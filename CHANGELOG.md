# Changelog

All notable changes to this project will be documented in this file.

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
