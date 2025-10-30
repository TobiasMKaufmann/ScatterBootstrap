"""
Python wrapper for core_multi_shell form factor C extension.
Handles array parameters for multiple shells.
"""

import ctypes
import numpy as np
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from finding_compiled_c_files import find_library

# Load the shared library
_lib_path = find_library("core_multi_shell", os.path.dirname(__file__))

if not os.path.exists(_lib_path):
    raise ImportError(
        f"Core_multi_shell shared library not found at {_lib_path}. "
        "Please build the extension by running: python setup.py build_py"
    )


# On Windows, add the lib directory to DLL search path so libsas_core.pyd can be found
if sys.platform == 'win32':
    lib_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "lib"))
    libsas_core_path = os.path.join(lib_dir, "libsas_core.pyd")
    
    # Preload the core library
    if os.path.exists(libsas_core_path):
        try:
            _core_lib = ctypes.CDLL(libsas_core_path)
        except Exception as e:
            print(f"Warning: Could not preload libsas_core.pyd: {e}")
    
    # Also add to DLL search path for Python 3.8+
    if hasattr(os, 'add_dll_directory'):
        os.add_dll_directory(lib_dir)

_lib = ctypes.CDLL(_lib_path)

# Define the Fq function signature
# void Fq(double q, double *F1, double *F2, double core_sld, double core_radius,
#    double solvent_sld, double fp_n, double sld[], double thickness[])
_lib.Fq.argtypes = [
    ctypes.c_double,  # q
    ctypes.POINTER(ctypes.c_double),  # F1
    ctypes.POINTER(ctypes.c_double),  # F2
    ctypes.c_double,  # core_sld
    ctypes.c_double,  # core_radius
    ctypes.c_double,  # solvent_sld
    ctypes.c_double,  # fp_n (number of shells)
    ctypes.POINTER(ctypes.c_double),  # sld array
    ctypes.POINTER(ctypes.c_double),  # thickness array
]
_lib.Fq.restype = None


def compute_form_factor(q, core_sld, core_radius, solvent_sld, n_shells, sld_array, thickness_array, **kwargs):
    """
    Compute the core_multi_shell form factor.
    
    Parameters
    ----------
    q : array_like
        The scattering vector magnitude(s) in inverse Angstroms (1/Å).
    core_sld : float
        Core scattering length density.
    core_radius : float
        Core radius.
    solvent_sld : float
        Solvent scattering length density.
    n_shells : int
        Number of shells.
    sld_array : array_like
        Array of shell SLDs.
    thickness_array : array_like
        Array of shell thicknesses.
    **kwargs : dict
        Additional keyword arguments (not used).
    
    Returns
    -------
    ndarray
        Form factor intensity I(q)
    """
    q = np.atleast_1d(q).astype(float)
    result = np.zeros_like(q)
    
    # Convert arrays to C arrays
    sld_arr = (ctypes.c_double * len(sld_array))(*sld_array)
    thickness_arr = (ctypes.c_double * len(thickness_array))(*thickness_array)
    
    f1 = ctypes.c_double()
    f2 = ctypes.c_double()
    
    for i, q_val in enumerate(q):
        _lib.Fq(
            ctypes.c_double(q_val),
            ctypes.byref(f1),
            ctypes.byref(f2),
            ctypes.c_double(core_sld),
            ctypes.c_double(core_radius),
            ctypes.c_double(solvent_sld),
            ctypes.c_double(n_shells),
            sld_arr,
            thickness_arr
        )
        result[i] = f2.value  # Return intensity (F^2)
    
    return result
