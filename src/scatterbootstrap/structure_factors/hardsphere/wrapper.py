"""
Python wrapper for hardsphere structure_factor C extension.
"""

import ctypes
import numpy as np
import os
import sys

from ..._lib_finder import find_library

# Load the shared library
_lib_path = find_library("hardsphere", os.path.dirname(__file__))

if not os.path.exists(_lib_path):
    raise ImportError(
        f"Hardsphere shared library not found at {_lib_path}. "
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
            ctypes.c_double(volfraction),
        )

    return result
