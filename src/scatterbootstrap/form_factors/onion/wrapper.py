"""
Python wrapper for onion form factor C extension.
"""

import ctypes
import numpy as np
import os
import sys

from ..._lib_finder import find_library

# Load the shared library
_lib_path = find_library("onion", os.path.dirname(__file__))

if not os.path.exists(_lib_path):
    raise ImportError(
        f"Onion shared library not found at {_lib_path}. "
        "Please build the extension by running: pip install -e ."
    )


# On Windows, add the lib directory to DLL search path so libsas_core.pyd can be found
if sys.platform == "win32":
    lib_dir = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "..", "lib")
    )
    libsas_core_path = os.path.join(lib_dir, "libsas_core.pyd")

    # Preload the core library
    if os.path.exists(libsas_core_path):
        try:
            _core_lib = ctypes.CDLL(libsas_core_path)
        except Exception as e:
            print(f"Warning: Could not preload libsas_core.pyd: {e}")

    # Also add to DLL search path for Python 3.8+
    if hasattr(os, "add_dll_directory"):
        os.add_dll_directory(lib_dir)

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


def compute_form_factor(
    q,
    sld_core,
    radius_core,
    sld_solvent,
    n_shells,
    sld_in,
    sld_out,
    thickness,
    A,
    **kwargs,
):
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
            A_arr,
        )
        result[i] = f2.value  # Return intensity (F^2)

    return result


__all__ = ["compute_form_factor"]
