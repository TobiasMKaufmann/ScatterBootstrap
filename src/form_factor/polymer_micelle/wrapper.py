"""
Python wrapper for polymer_micelle form_factor C extension.
"""

import ctypes
import numpy as np
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from finding_compiled_c_files import find_library

# Load the shared library
_lib_path = find_library("polymer_micelle", os.path.dirname(__file__))

if not os.path.exists(_lib_path):
    raise ImportError(
        f"Polymer_micelle shared library not found at {_lib_path}. "
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

# Define the Iq function signature (returns double directly)
_lib.Iq.argtypes = [
        ctypes.c_double,  # q,
        ctypes.c_double,  # ndensity,
        ctypes.c_double,  # v_core,
        ctypes.c_double,  # v_corona,
        ctypes.c_double,  # solvent_sld,
        ctypes.c_double,  # core_sld,
        ctypes.c_double,  # corona_sld,
        ctypes.c_double,  # radius_core,
        ctypes.c_double,  # rg,
        ctypes.c_double,  # d_penetration,
        ctypes.c_double,  # n_aggreg
    ]
_lib.Iq.restype = ctypes.c_double


def compute_form_factor(q, ndensity, v_core, v_corona, solvent_sld, core_sld, corona_sld, radius_core, rg, d_penetration, n_aggreg, **kwargs):
    """
    Compute the polymer_micelle form factor.
    
    Parameters
    ----------
    q : array_like
        The scattering vector magnitude(s) in inverse Angstroms (1/Å).
    ndensity : float
        Parameter ndensity.
    v_core : float
        Parameter v_core.
    v_corona : float
        Parameter v_corona.
    solvent_sld : float
        Parameter solvent_sld.
    core_sld : float
        Parameter core_sld.
    corona_sld : float
        Parameter corona_sld.
    radius_core : float
        Parameter radius_core.
    rg : float
        Parameter rg.
    d_penetration : float
        Parameter d_penetration.
    n_aggreg : float
        Parameter n_aggreg.
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
            ctypes.c_double(ndensity),
            ctypes.c_double(v_core),
            ctypes.c_double(v_corona),
            ctypes.c_double(solvent_sld),
            ctypes.c_double(core_sld),
            ctypes.c_double(corona_sld),
            ctypes.c_double(radius_core),
            ctypes.c_double(rg),
            ctypes.c_double(d_penetration),
            ctypes.c_double(n_aggreg)
        )
    
    return result
