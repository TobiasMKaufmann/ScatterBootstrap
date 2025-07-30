import ctypes
import os

# Load the shared library
lib_path = os.path.join(os.path.dirname(__file__), 'hayter_msa.so')
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
    q : float
        Scattering vector (1/Å)
    radius_effective : float
        Effective radius (Å)
    volume_fraction : float
        Volume fraction (dimensionless)
    charge : float
        Particle charge (elementary charges)
    temperature : float
        Temperature (K)
    salt_concentration : float
        Salt concentration (M)
    dielectric_constant : float
        Dielectric constant (dimensionless)
    
    Returns:
    float
        Structure factor S(q)
    """
    return lib.Iq(q, radius_effective, volume_fraction, charge, temperature, salt_concentration, dielectric_constant)
