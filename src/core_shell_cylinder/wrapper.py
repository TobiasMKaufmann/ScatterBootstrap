from ctypes import CDLL, c_double, POINTER
import os
import sys
from pathlib import Path

def find_library(base_name):
    """Find the compiled library file, handling platform-specific naming.
    
    Supports various naming conventions:
    - Simple: module.so, module.pyd
    - Python version: module.cp312.so, module.cp311-win_amd64.pyd
    - Full platform: module.cpython-312-x86_64-linux-gnu.so
    - macOS: module.cpython-312-darwin.so
    - Legacy: module.dll
    """
    import glob
    current_dir = os.path.dirname(__file__)
    
    # Try exact names first (preferred for custom builds)
    if sys.platform == 'win32':
        exact_names = [f'{base_name}.pyd', f'{base_name}.dll']
    else:
        exact_names = [f'{base_name}.so']
    
    for exact_name in exact_names:
        exact_path = os.path.join(current_dir, exact_name)
        if os.path.exists(exact_path):
            return exact_path
    
    # If exact name doesn't exist, search for platform-specific names
    # These patterns cover all common setuptools/distutils naming conventions
    patterns = [
        # Python version + platform (Windows): module.cp312-win_amd64.pyd
        os.path.join(current_dir, f'{base_name}.cp*-*.pyd'),
        # Python version only (Windows): module.cp312.pyd
        os.path.join(current_dir, f'{base_name}.cp*.pyd'),
        # Full cpython naming (Linux/Mac): module.cpython-312-x86_64-linux-gnu.so
        os.path.join(current_dir, f'{base_name}.cpython-*-*.so'),
        # Python version + platform (Linux/Mac): module.cp312-linux_x86_64.so
        os.path.join(current_dir, f'{base_name}.cp*-*.so'),
        # Python version only (Linux/Mac): module.cp312.so
        os.path.join(current_dir, f'{base_name}.cp*.so'),
        # Any .so file starting with base_name (catch-all for Unix)
        os.path.join(current_dir, f'{base_name}.*.so'),
        # Any .pyd file starting with base_name (catch-all for Windows)
        os.path.join(current_dir, f'{base_name}.*.pyd'),
    ]
    
    for pattern in patterns:
        matches = glob.glob(pattern)
        if matches:
            # Sort to prefer shorter names (more specific Python versions come first)
            matches.sort(key=lambda x: len(os.path.basename(x)))
            return matches[0]
    
    # If still not found, raise informative error with searched patterns
    raise FileNotFoundError(
        f"Could not find compiled library '{base_name}' in {current_dir}.\n"
        f"Searched for patterns: {exact_names[0]}, {base_name}.cp*.so/pyd, {base_name}.cpython-*.so/pyd\n"
        f"Make sure to run 'pip install -e .' or 'python setup.py build_ext --inplace' first."
    )

lib_path = find_library('core_shell_cylinder')
core_shell_lib = CDLL(lib_path)

def compute_form_factor(q, core_sld, shell_sld, solvent_sld, radius, thickness, length):
    """
    Compute the form factor for the core-shell cylinder model.

    Parameters:
    q (float): The scattering vector magnitude.
    core_sld (float): The scattering length density of the core.
    shell_sld (float): The scattering length density of the shell.
    solvent_sld (float): The scattering length density of the solvent.
    radius (float): The radius of the core.
    thickness (float): The thickness of the shell.
    length (float): The length of the cylinder.

    Returns:
    float: The computed form factor.
    """
    F1 = c_double()
    F2 = c_double()

    core_shell_lib.Fq(
        c_double(q),
        POINTER(c_double)(F1),
        POINTER(c_double)(F2),
        c_double(core_sld),
        c_double(shell_sld),
        c_double(solvent_sld),
        c_double(radius),
        c_double(thickness),
        c_double(length)
    )

    return F1.value, F2.value