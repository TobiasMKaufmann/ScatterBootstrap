import ctypes
import os
import sys

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
    # Pattern: base_name.cp###-platform.so/pyd or base_name.cpython-##-platform.so/pyd
    patterns = [
        os.path.join(current_dir, f'{base_name}.cp*'),      # Matches .cp311-win_amd64.pyd
        os.path.join(current_dir, f'{base_name}.cpython-*'), # Matches .cpython-311-x86_64-linux-gnu.so
    ]
    
    for pattern in patterns:
        matches = glob.glob(pattern)
        # Filter out exact match (already checked) and only keep platform-specific names
        matches = [m for m in matches if not m.endswith(exact_name)]
        if matches:
            return matches[0]  # Return the first match
    
    # If still not found, raise informative error
    raise FileNotFoundError(
        f"Could not find compiled library '{base_name}' in {current_dir}. "
        f"Expected '{exact_name}' or platform-specific variant. "
        f"Make sure to run 'pip install -e .' or 'python setup.py build_ext --inplace' first."
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
