"""
Python wrapper for hardsphere structure_factor C extension.
"""

import ctypes
import numpy as np
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from finding_compiled_c_files import find_library

# Load the shared library
_lib_path = find_library("hardsphere", os.path.dirname(__file__))

if not os.path.exists(_lib_path):
    raise ImportError(
        f"Hardsphere shared library not found at {_lib_path}. "
        "Please build the extension by running: python setup.py build_py"
    )

_lib = ctypes.CDLL(_lib_path)

# Define the Iq function signature (returns double directly)
_lib.Iq.argtypes = [
        ctypes.c_double,  # q,
        ctypes.c_double,  # radius_effective,
        ctypes.c_double,  # volfraction
    ]
_lib.Iq.restype = ctypes.c_double


def compute_structure_factor(q, radius_effective, volfraction, **kwargs):
    """
    Compute the hardsphere structure factor.
    
    Parameters
    ----------
    q : array_like
        The scattering vector magnitude(s) in inverse Angstroms (1/Å).
    radius_effective : float
        Parameter radius_effective.
    volfraction : float
        Parameter volfraction.
    **kwargs : dict
        Additional keyword arguments (not used).
    
    Returns
    -------
    ndarray
        Structure factor S(q)
    """
    q = np.atleast_1d(q).astype(float)
    result = np.zeros_like(q)
    
    for i, q_val in enumerate(q):
        result[i] = _lib.Iq(
            ctypes.c_double(q_val),
            ctypes.c_double(radius_effective),
            ctypes.c_double(volfraction)
        )
    
    return result
