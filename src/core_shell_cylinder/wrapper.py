from ctypes import CDLL, c_double, POINTER
import os
import sys
from pathlib import Path

def find_library(base_name):
    """Find the compiled library file, handling platform-specific naming."""
    import glob
    current_dir = os.path.dirname(__file__)
    
    # Try exact names first
    if sys.platform == 'win32':
        exact_name = f'{base_name}.pyd'
    else:
        exact_name = f'{base_name}.so'
    
    exact_path = os.path.join(current_dir, exact_name)
    if os.path.exists(exact_path):
        return exact_path
    
    # If exact name doesn't exist, search for platform-specific names
    # Pattern: base_name.cpython-*-(platform).so/pyd
    pattern = os.path.join(current_dir, f'{base_name}.cpython-*')
    matches = glob.glob(pattern)
    
    if matches:
        return matches[0]  # Return the first match
    
    # If still not found, raise informative error
    raise FileNotFoundError(
        f"Could not find compiled library '{base_name}' in {current_dir}. "
        f"Expected '{exact_name}' or platform-specific variant. "
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