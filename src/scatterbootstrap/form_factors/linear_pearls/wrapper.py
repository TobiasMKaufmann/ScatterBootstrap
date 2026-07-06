"""
Python wrapper for linear_pearls form_factor C extension.
"""

import ctypes
import numpy as np
import os
import sys

from ..._lib_finder import find_library

# Load the shared library
_lib_path = find_library("linear_pearls", os.path.dirname(__file__))

if not os.path.exists(_lib_path):
    raise ImportError(
        f"Linear_pearls shared library not found at {_lib_path}. "
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
    ctypes.c_double,  # radius,
    ctypes.c_double,  # edge_sep,
    ctypes.c_double,  # fp_num_pearls,
    ctypes.c_double,  # pearl_sld,
    ctypes.c_double,  # solvent_sld
]
_lib.Iq.restype = ctypes.c_double


def compute_form_factor(
    q, radius, edge_sep, fp_num_pearls, pearl_sld, solvent_sld, **kwargs
):
    """
    Compute the linear_pearls form factor.

    Parameters
    ----------
    q : array_like
        The scattering vector magnitude(s) in inverse Angstroms (1/Å).
    radius : float
        Parameter radius.
    edge_sep : float
        Parameter edge_sep.
    fp_num_pearls : float
        Parameter fp_num_pearls.
    pearl_sld : float
        Parameter pearl_sld.
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
            ctypes.c_double(radius),
            ctypes.c_double(edge_sep),
            ctypes.c_double(fp_num_pearls),
            ctypes.c_double(pearl_sld),
            ctypes.c_double(solvent_sld),
        )

    return result
