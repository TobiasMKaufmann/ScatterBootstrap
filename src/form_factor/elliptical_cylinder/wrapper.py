"""
Python wrapper for elliptical_cylinder form_factor C extension.
"""

import ctypes
import numpy as np
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from finding_compiled_c_files import find_library

# Load the shared library
_lib_path = find_library("elliptical_cylinder", os.path.dirname(__file__))

if not os.path.exists(_lib_path):
    raise ImportError(
        f"Elliptical_cylinder shared library not found at {_lib_path}. "
        "Please build the extension by running: python setup.py build_py"
    )

_lib = ctypes.CDLL(_lib_path)

# Define the Fq function signature
_lib.Fq.argtypes = [
        ctypes.c_double,  # q,
        ctypes.POINTER(ctypes.c_double),  # f1,
        ctypes.POINTER(ctypes.c_double),  # f2,
        ctypes.c_double,  # radius_minor,
        ctypes.c_double,  # r_ratio,
        ctypes.c_double,  # length,
        ctypes.c_double,  # sld,
        ctypes.c_double,  # solvent_sld
    ]
_lib.Fq.restype = None


def compute_form_factor(q, radius_minor, r_ratio, length, sld, solvent_sld, **kwargs):
    """
    Compute the elliptical_cylinder form factor.
    
    Parameters
    ----------
    q : array_like
        The scattering vector magnitude(s) in inverse Angstroms (1/Å).
    radius_minor : float
        Parameter radius_minor.
    r_ratio : float
        Parameter r_ratio.
    length : float
        Parameter length.
    sld : float
        Parameter sld.
    solvent_sld : float
        Parameter solvent_sld.
    **kwargs : dict
        Additional keyword arguments (not used).
    
    Returns
    -------
    ndarray
        Form factor intensity I(q)
    """
    q = np.atleast_1d(q).astype(float)
    result = np.zeros_like(q)
    
    f1 = ctypes.c_double()
    f2 = ctypes.c_double()
    
    for i, q_val in enumerate(q):
        _lib.Fq(
            ctypes.c_double(q_val),
            ctypes.byref(f1),
            ctypes.byref(f2),
            ctypes.c_double(radius_minor),
            ctypes.c_double(r_ratio),
            ctypes.c_double(length),
            ctypes.c_double(sld),
            ctypes.c_double(solvent_sld)
        )
        result[i] = f2.value  # Return intensity (F^2)
    
    return result
