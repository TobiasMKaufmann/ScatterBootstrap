"""
Python wrapper for fcc_paracrystal form_factor C extension.
"""

import ctypes
import numpy as np
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from finding_compiled_c_files import find_library

# Load the shared library
_lib_path = find_library("fcc_paracrystal", os.path.dirname(__file__))

if not os.path.exists(_lib_path):
    raise ImportError(
        f"Fcc_paracrystal shared library not found at {_lib_path}. "
        "Please build the extension by running: python setup.py build_py"
    )

_lib = ctypes.CDLL(_lib_path)

# Define the Iq function signature (returns double directly)
_lib.Iq.argtypes = [
        ctypes.c_double,  # q,
        ctypes.c_double,  # dnn,
        ctypes.c_double,  # d_factor,
        ctypes.c_double,  # radius,
        ctypes.c_double,  # sld,
        ctypes.c_double,  # solvent_sld
    ]
_lib.Iq.restype = ctypes.c_double


def compute_form_factor(q, dnn, d_factor, radius, sld, solvent_sld, **kwargs):
    """
    Compute the fcc_paracrystal form factor.
    
    Parameters
    ----------
    q : array_like
        The scattering vector magnitude(s) in inverse Angstroms (1/Å).
    dnn : float
        Parameter dnn.
    d_factor : float
        Parameter d_factor.
    radius : float
        Parameter radius.
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
    
    for i, q_val in enumerate(q):
        result[i] = _lib.Iq(
            ctypes.c_double(q_val),
            ctypes.c_double(dnn),
            ctypes.c_double(d_factor),
            ctypes.c_double(radius),
            ctypes.c_double(sld),
            ctypes.c_double(solvent_sld)
        )
    
    return result
