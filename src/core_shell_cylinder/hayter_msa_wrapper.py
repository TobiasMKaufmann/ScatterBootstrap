import ctypes
import os
import sys

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
