from ctypes import CDLL, c_double, POINTER
import os
import sys
from pathlib import Path

# TODO: Too permissive at the moment
def find_library(base_name):
    """Find the compiled library file, handling platform-specific naming.
    
    Searches for library files with various extensions (.so, .pyd, .dll) and
    naming patterns (simple names and platform-specific setuptools names).
    """
    import glob
    current_dir = os.path.dirname(__file__)
    
    # Build list of all possible patterns to search, in priority order
    # Windows: .pyd and .dll extensions
    # Linux/Mac: .so extension
    extension_patterns = []
    if sys.platform == 'win32':
        extension_patterns = ['pyd', 'dll']
    else:
        extension_patterns = ['so']
    
    # Collect all candidate files
    candidates = []
    for ext in extension_patterns:
        # Pattern matches: any file containing base_name with the correct extension
        pattern = os.path.join(current_dir, f'*{base_name}*.{ext}')
        candidates.extend(glob.glob(pattern))
    
    # Sort by filename length (prefer simpler names)
    candidates.sort(key=lambda x: len(os.path.basename(x)))
    
    # Return the first match or raise error
    if candidates:
        return candidates[0]
    
    raise FileNotFoundError(
        f"Could not find compiled library '{base_name}' in {current_dir}.\n"
        f"Expected files like: {base_name}.so, {base_name}.pyd, or platform-specific variants.\n"
        f"Make sure to run 'pip install -e .' or 'python setup.py build_py' first."
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