"""
Python wrapper for onion form factor C extension.
"""

import ctypes
import numpy as np
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from finding_compiled_c_files import find_library

# Load the shared library
_lib_path = find_library("onion", os.path.dirname(__file__))

if not os.path.exists(_lib_path):
    raise ImportError(
        f"Onion shared library not found at {_lib_path}. "
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
# void Fq(double q, double *F1, double *F2, double sld_core, double radius_core, 
#         double sld_solvent, double n_shells, double sld_in[], double sld_out[], 
#         double thickness[], double A[])
_lib.Fq.argtypes = [
    ctypes.c_double,  # q
    ctypes.POINTER(ctypes.c_double),  # F1
    ctypes.POINTER(ctypes.c_double),  # F2
    ctypes.c_double,  # sld_core
    ctypes.c_double,  # radius_core
    ctypes.c_double,  # sld_solvent
    ctypes.c_double,  # n_shells
    ctypes.POINTER(ctypes.c_double),  # sld_in[]
    ctypes.POINTER(ctypes.c_double),  # sld_out[]
    ctypes.POINTER(ctypes.c_double),  # thickness[]
    ctypes.POINTER(ctypes.c_double),  # A[]
]
_lib.Fq.restype = None


def compute_form_factor(q, core_radius, core_sld, solvent_sld,
                       shell1_thickness, shell1_sld,
                       shell2_thickness=0.0, shell2_sld=0.0,
                       shell3_thickness=0.0, shell3_sld=0.0,
                       shell4_thickness=0.0, shell4_sld=0.0):
    """
    Compute the onion form factor (multi-shell sphere).
    
    Parameters
    ----------
    q : array_like
        The scattering vector magnitude(s) in inverse Angstroms (1/Å).
    core_radius : float
        Radius of the core (Å).
    core_sld : float
        Core scattering length density (10^-6 Å^-2).
    solvent_sld : float
        Solvent scattering length density (10^-6 Å^-2).
    shell1_thickness : float
        Thickness of shell 1 (Å).
    shell1_sld : float
        SLD of shell 1 (10^-6 Å^-2).
    shell2_thickness : float, optional
        Thickness of shell 2 (Å).
    shell2_sld : float, optional
        SLD of shell 2 (10^-6 Å^-2).
    shell3_thickness : float, optional
        Thickness of shell 3 (Å).
    shell3_sld : float, optional
        SLD of shell 3 (10^-6 Å^-2).
    shell4_thickness : float, optional
        Thickness of shell 4 (Å).
    shell4_sld : float, optional
        SLD of shell 4 (10^-6 Å^-2).
    
    Returns
    -------
    ndarray
        Form factor intensity I(q)
    """
    q = np.atleast_1d(q).astype(float)
    result = np.zeros_like(q)
    
    # Build arrays for shells (up to 4 shells)
    thicknesses = [shell1_thickness, shell2_thickness, shell3_thickness, shell4_thickness]
    slds = [shell1_sld, shell2_sld, shell3_sld, shell4_sld]
    
    # Count non-zero shells
    n_shells = sum(1 for t in thicknesses if t > 0)
    
    # Prepare arrays (onion needs sld_in, sld_out, thickness, A for each shell)
    thickness_arr = (ctypes.c_double * n_shells)(*thicknesses[:n_shells])
    sld_in_arr = (ctypes.c_double * n_shells)(*slds[:n_shells])
    sld_out_arr = (ctypes.c_double * n_shells)(*slds[:n_shells])
    A_arr = (ctypes.c_double * n_shells)(*([0.0] * n_shells))  # A=0 for flat interfaces
    
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
            sld_in_arr,
            sld_out_arr,
            thickness_arr,
            A_arr
        )
        result[i] = f2.value  # Return intensity (F^2)
    
    return result

import ctypes
import numpy as np
import os
import sys

# Determine the library filename based on platform
if sys.platform == 'win32':
    _lib_name = 'onion.pyd'
else:
    _lib_name = 'onion.so'

# Load the shared library
_lib_path = os.path.join(os.path.dirname(__file__), _lib_name)

if not os.path.exists(_lib_path):
    raise ImportError(
        f"Onion shared library not found at {_lib_path}. "
        "Please build the extension by running: python setup.py build_py"
    )

_lib = ctypes.CDLL(_lib_path)

# Define the Fq function signature
# void Fq(double q, double *F1, double *F2, double sld_core, double radius_core, double sld_solvent,
#     double n_shells, double sld_in[], double sld_out[], double thickness[], double A[])
_lib.Fq.argtypes = [
    ctypes.c_double,  # q
    ctypes.POINTER(ctypes.c_double),  # F1
    ctypes.POINTER(ctypes.c_double),  # F2
    ctypes.c_double,  # sld_core
    ctypes.c_double,  # radius_core
    ctypes.c_double,  # sld_solvent
    ctypes.c_double,  # n_shells
    ctypes.POINTER(ctypes.c_double),  # sld_in array
    ctypes.POINTER(ctypes.c_double),  # sld_out array
    ctypes.POINTER(ctypes.c_double),  # thickness array
    ctypes.POINTER(ctypes.c_double),  # A array
]
_lib.Fq.restype = None


def compute_form_factor(q, sld_core, radius_core, sld_solvent, n_shells, 
                       sld_in, sld_out, thickness, A, **kwargs):
    """
    Compute the onion form factor.
    
    Parameters
    ----------
    q : array_like
        The scattering vector magnitude(s) in inverse Angstroms (1/Å).
    sld_core : float
        Core scattering length density.
    radius_core : float
        Core radius.
    sld_solvent : float
        Solvent scattering length density.
    n_shells : int
        Number of shells.
    sld_in : array_like
        Array of inner shell SLDs.
    sld_out : array_like
        Array of outer shell SLDs.
    thickness : array_like
        Array of shell thicknesses.
    A : array_like
        Array of A parameters (interface width).
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
    sld_in_arr = (ctypes.c_double * len(sld_in))(*sld_in)
    sld_out_arr = (ctypes.c_double * len(sld_out))(*sld_out)
    thickness_arr = (ctypes.c_double * len(thickness))(*thickness)
    A_arr = (ctypes.c_double * len(A))(*A)
    
    f1 = ctypes.c_double()
    f2 = ctypes.c_double()
    
    for i, q_val in enumerate(q):
        _lib.Fq(
            ctypes.c_double(q_val),
            ctypes.byref(f1),
            ctypes.byref(f2),
            ctypes.c_double(sld_core),
            ctypes.c_double(radius_core),
            ctypes.c_double(sld_solvent),
            ctypes.c_double(n_shells),
            sld_in_arr,
            sld_out_arr,
            thickness_arr,
            A_arr
        )
        result[i] = f2.value  # Return intensity (F^2)
    
    return result


__all__ = ['compute_form_factor']
