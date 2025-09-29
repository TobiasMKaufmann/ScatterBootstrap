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
    pip_available = run_command(f"{sys.executable} -c 'import pip'")
    
    if pip_available:
        print("✓ pip is available, installing packages")
        install_commands = [
            f"{sys.executable} -m pip install --user numpy",
            f"{sys.executable} -m pip install --user pandas", 
            f"{sys.executable} -m pip install --user scipy",
            f"{sys.executable} -m pip install --user h5py",
            f"{sys.executable} -m pip install --user tables",  # for pandas HDF5
            f"{sys.executable} -m pip install --user tqdm",
            f"{sys.executable} -m pip install --user matplotlib",
        ]
        
        for cmd in install_commands:
            print(f"Running: {cmd}")
            if not run_command(cmd):
                print(f"Warning: Failed to install package: {cmd}")
            else:
                print("✓ Package installed successfully")
    else:
        print("✗ pip not available even with module loaded")
    
    # Handle C extensions in src/core_shell_cylinder
    print("Checking C extensions...")
    c_ext_dir = "../core_shell_cylinder"
    
    if os.path.exists(c_ext_dir):
        print(f"Found C extension directory: {c_ext_dir}")
        
        # Always recompile .so files on cluster for compatibility
        print("Recompiling C extensions for cluster compatibility...")
        
        # Remove existing .so files first
        so_files = ["core_shell_cylinder.so", "libcore_shell_cylinder.so", "hayter_msa.so"]
        for so_file in so_files:
            so_path = os.path.join(c_ext_dir, so_file)
            if os.path.exists(so_path):
                os.remove(so_path)
                print(f"Removed {so_file}")
        
        compile_commands = [
            f"cd {c_ext_dir} && gcc -shared -fPIC -O3 -Wall -o core_shell_cylinder.so core_shell_cylinder.c gauss76.c sas_J1.c polevl.c utils.c -lm",
            f"cd {c_ext_dir} && gcc -shared -fPIC -O3 -Wall -o hayter_msa.so hayter_msa.c utils.c -lm",
            f"cd {c_ext_dir} && cp core_shell_cylinder.so libcore_shell_cylinder.so",
            f"cd {c_ext_dir} && cp hayter_msa.so libhayter_msa.so"
        ]
        
        for cmd in compile_commands:
            print(f"Running: {cmd}")
            if not run_command(cmd):
                print(f"Warning: Compilation failed for: {cmd}")
            else:
                print(f"✓ Compiled successfully")
        
        # Test if C extensions can be imported
        print("Testing C extension imports...")
        test_cmd = f"cd {c_ext_dir} && {sys.executable} -c 'import wrapper; print(\"C extension loaded successfully\")'"
        if not run_command(test_cmd):
            print("Warning: C extension import failed")
        else:
            print("✓ C extensions working")
    
    else:
        print(f"Warning: C extension directory {c_ext_dir} not found")
    
    # Test if we can import all required packages
    print("Testing package availability...")
    test_imports = [
        "import numpy",
        "import pandas", 
        "import scipy",
        "import scipy.optimize",
        "import h5py",
        "import tables",  # PyTables for pandas HDF5 support
        "import tqdm",
        "import Cython",
        "import json",
        "import glob",
        "import os",
        "import sys"
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
