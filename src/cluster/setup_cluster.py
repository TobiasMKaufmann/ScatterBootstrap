"""
Cluster Environment Setup and C Extension Builder

This script handles the automated setup of the Python environment and C extensions
for the ScatterBootstrap package on ETH HPC systems. It ensures all necessary
dependencies are installed and C extensions are properly compiled for the cluster
architecture.

Key Functions:
=============

Dependency Management:
- Automatic detection of available Python and pip
- User-space installation of required Python packages
- Fallback mechanisms for different cluster configurations
- Compatibility with ETH HPC module system

C Extension Handling:
- Automatic detection of existing compiled extensions
- Cross-platform compilation with appropriate flags
- Cleanup of incompatible binaries from local builds
- Verification of successful compilation

Error Recovery:
- Graceful handling of missing system packages
- Alternative installation methods for restricted environments
- Detailed logging of setup progress and issues
- Non-fatal warnings for optional dependencies

Cluster Compatibility:
- Optimized for ETH HPC (Euler/Leonhard) systems
- Compatible with standard Linux HPC environments
- Works with both system and module-based Python installations
- Handles restricted user permissions appropriately

Required System Components:
- Python 3.8+ with development headers
- C compiler (gcc or clang)
- Standard build tools (make, etc.)
- Network access for package downloads

Generated Files:
- Compiled C extensions (.so files)
- User-space Python package installations
- Setup verification logs

Usage:
    python setup_cluster.py

This script is automatically called by submit_job.sh during job execution.
"""

import subprocess
import sys
import os

def run_command(cmd):
    """Run shell command and return output"""
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error running: {cmd}")
        print(result.stderr)
        return False
    return True

def setup_environment():
    """Setup Python environment for ETH HPC"""
    print("Setting up environment for ETH HPC...")
    
    # Check if pip is available with the loaded module
    print("Checking for pip with loaded module...")
    if not run_command(f"{sys.executable} -c 'import pip'"):
        print("✗ pip not available even with module loaded")
        sys.exit(1)

    # Install the package itself (editable, user-space). This pulls all runtime
    # dependencies from pyproject.toml AND compiles every C extension
    # (libsas_core + all form/structure factor models) for the cluster's
    # architecture via the project's own build system -- no hand-maintained
    # compiler commands.
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    print(f"Installing ScatterBootstrap (with C extensions) from {repo_root} ...")
    if not run_command(f"{sys.executable} -m pip install --user -e {repo_root}"):
        print("✗ Package installation failed")
        sys.exit(1)
    print("✓ Package installed, C extensions compiled")

    # Verify the installed package: import, model discovery, and one evaluation
    # through a compiled C kernel.
    print("Verifying compiled extensions...")
    verify = (
        "import scatterbootstrap as sb; "
        "ffs = sb.list_form_factor_models(); sfs = sb.list_structure_factor_models(); "
        "assert ffs and sfs, 'no models discovered'; "
        "val = sb.form_factor(0.1, 'sphere', sld=4e-6, sld_solvent=1e-6, radius=50); "
        "print(f'  {len(ffs)} form factors, {len(sfs)} structure factors, sphere F2(0.1)={val:.3e}')"
    )
    if not run_command(f'{sys.executable} -c "{verify}"'):
        print("✗ Compiled extension verification failed")
        sys.exit(1)
    print("✓ C extensions working")

    # Test the auxiliary packages the cluster pipeline needs.
    print("Testing package availability...")
    test_imports = [
        "import numpy",
        "import pandas",
        "import scipy.optimize",
        "import tables",  # PyTables for pandas HDF5 support
        "import tqdm",
    ]

    for test_import in test_imports:
        if not run_command(f"{sys.executable} -c '{test_import}'"):
            print(f"✗ Failed to import: {test_import}")
        else:
            print(f"✓ {test_import}")
    
    # Test pandas HDF5 functionality specifically
    print("Testing pandas HDF5 support...")
    hdf5_test = "import pandas as pd; store = pd.HDFStore('/tmp/test.h5', 'w'); store.close(); import os; os.remove('/tmp/test.h5')"
    if not run_command(f"{sys.executable} -c \"{hdf5_test}\""):
        print("✗ pandas HDF5 support not working")
    else:
        print("✓ pandas HDF5 support working")
    
    print("Setup complete!")

if __name__ == "__main__":
    setup_environment()
