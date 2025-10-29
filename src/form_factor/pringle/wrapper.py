"""
Python wrapper for pringle form_factor C extension.
"""

import ctypes
import numpy as np
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from finding_compiled_c_files import find_library

# Load the shared library
_lib_path = find_library("pringle", os.path.dirname(__file__))

if not os.path.exists(_lib_path):
    raise ImportError(
        f"Pringle shared library not found at {_lib_path}. "
        "Please build the extension by running: python setup.py build_py"
    )

_lib = ctypes.CDLL(_lib_path)

# Define the Iq function signature (returns double directly)
_lib.Iq.argtypes = [
        ctypes.c_double,  # q,
        ctypes.c_double,  # radius,
        ctypes.c_double,  # thickness,
        ctypes.c_double,  # alpha,
        ctypes.c_double,  # beta,
        ctypes.c_double,  # sld,
        ctypes.c_double,  # sld_solvent
    ]
_lib.Iq.restype = ctypes.c_double


def compute_form_factor(q, radius, thickness, alpha, beta, sld, sld_solvent, **kwargs):
    """
    Compute the pringle form factor.
    
    Parameters
    ----------
    q : array_like
        The scattering vector magnitude(s) in inverse Angstroms (1/Å).
    radius : float
        Parameter radius.
    thickness : float
        Parameter thickness.
    alpha : float
        Parameter alpha.
    beta : float
        Parameter beta.
    sld : float
        Parameter sld.
    sld_solvent : float
        Parameter sld_solvent.
    **kwargs : dict
        Additional keyword arguments (not used).
    
    Returns
    -------
    ndarray
        Form factor intensity I(q)
    """
    q = np.atleast_1d(q).astype(float)
    result = np.zeros_like(q)
    
    for i, q_val in enumerate(q):
        result[i] = _lib.Iq(
            ctypes.c_double(q_val),
            ctypes.c_double(radius),
            ctypes.c_double(thickness),
            ctypes.c_double(alpha),
            ctypes.c_double(beta),
            ctypes.c_double(sld),
            ctypes.c_double(sld_solvent)
        )
    
    return result
