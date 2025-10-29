"""
Python wrapper for lamellar_hg form_factor C extension.
"""

import ctypes
import numpy as np
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from finding_compiled_c_files import find_library

# Load the shared library
_lib_path = find_library("lamellar_hg", os.path.dirname(__file__))

if not os.path.exists(_lib_path):
    raise ImportError(
        f"Lamellar_hg shared library not found at {_lib_path}. "
        "Please build the extension by running: python setup.py build_py"
    )

_lib = ctypes.CDLL(_lib_path)

# Define the Iq function signature (returns double directly)
_lib.Iq.argtypes = [
        ctypes.c_double,  # q,
        ctypes.c_double,  # length_tail,
        ctypes.c_double,  # length_head,
        ctypes.c_double,  # sld,
        ctypes.c_double,  # sld_head,
        ctypes.c_double,  # sld_solvent
    ]
_lib.Iq.restype = ctypes.c_double


def compute_form_factor(q, length_tail, length_head, sld, sld_head, sld_solvent, **kwargs):
    """
    Compute the lamellar_hg form factor.
    
    Parameters
    ----------
    q : array_like
        The scattering vector magnitude(s) in inverse Angstroms (1/Å).
    length_tail : float
        Parameter length_tail.
    length_head : float
        Parameter length_head.
    sld : float
        Parameter sld.
    sld_head : float
        Parameter sld_head.
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
            ctypes.c_double(length_tail),
            ctypes.c_double(length_head),
            ctypes.c_double(sld),
            ctypes.c_double(sld_head),
            ctypes.c_double(sld_solvent)
        )
    
    return result
