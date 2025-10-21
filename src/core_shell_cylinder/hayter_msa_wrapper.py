import ctypes
import os
import sys


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

lib_path = find_library('hayter_msa')
lib = ctypes.CDLL(lib_path)


# Define the function signature
lib.Iq.argtypes = [
    ctypes.c_double,  # QQ (scattering vector)
    ctypes.c_double,  # radius_effective
    ctypes.c_double,  # VolFrac (volume fraction)
    ctypes.c_double,  # zz (charge)
    ctypes.c_double,  # Temp (temperature)
    ctypes.c_double,  # csalt (salt concentration)
    ctypes.c_double   # dialec (dielectric constant)
]
lib.Iq.restype = ctypes.c_double

def compute_structure_factor(q, radius_effective, volume_fraction, charge, temperature, salt_concentration, dielectric_constant):
    """
    Compute the Hayter-Penfold MSA structure factor.
    
    Parameters:
    q (float): Scattering vector (1/Å)
    radius_effective (float): Effective radius (Å)
    volume_fraction (float): Volume fraction (dimensionless)
    charge (float): Particle charge (elementary charges)
    temperature (float): Temperature (K)
    salt_concentration (float): Salt concentration (M)
    dielectric_constant (float): Dielectric constant (dimensionless)
    
    Returns:
    float: Structure factor S(q)
    """
    return lib.Iq(q, radius_effective, volume_fraction, charge, temperature, salt_concentration, dielectric_constant)
