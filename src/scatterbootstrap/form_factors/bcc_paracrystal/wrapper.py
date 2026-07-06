"""
Python wrapper for bcc_paracrystal form_factor C extension.
"""

import ctypes
import numpy as np
import os
import sys

from ..._lib_finder import find_library

# Load the shared library
_lib_path = find_library("bcc_paracrystal", os.path.dirname(__file__))

if not os.path.exists(_lib_path):
    raise ImportError(
        f"Bcc_paracrystal shared library not found at {_lib_path}. "
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
    ctypes.c_double,  # dnn,
    ctypes.c_double,  # d_factor,
    ctypes.c_double,  # radius,
    ctypes.c_double,  # sld,
    ctypes.c_double,  # solvent_sld
]
_lib.Iq.restype = ctypes.c_double


def compute_form_factor(q, dnn, d_factor, radius, sld, solvent_sld, **kwargs):
    """
    Compute the bcc_paracrystal form factor.

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
            ctypes.c_double(solvent_sld),
        )

    return result
