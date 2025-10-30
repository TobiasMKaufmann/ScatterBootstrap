"""
Python wrapper for fuzzy_sphere form_factor C extension.
"""

import ctypes
import numpy as np
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from finding_compiled_c_files import find_library

# Load the shared library
_lib_path = find_library("fuzzy_sphere", os.path.dirname(__file__))

if not os.path.exists(_lib_path):
    raise ImportError(
        f"Fuzzy_sphere shared library not found at {_lib_path}. "
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

# Define the Fq function signature
_lib.Fq.argtypes = [
        ctypes.c_double,  # q,
        ctypes.POINTER(ctypes.c_double),  # f1,
        ctypes.POINTER(ctypes.c_double),  # f2,
        ctypes.c_double,  # sld,
        ctypes.c_double,  # sld_solvent,
        ctypes.c_double,  # radius,
        ctypes.c_double,  # fuzziness
    ]
_lib.Fq.restype = None


def compute_form_factor(q, sld, sld_solvent, radius, fuzziness, **kwargs):
    """
    Compute the fuzzy_sphere form factor.
    
    Parameters
    ----------
    q : array_like
        The scattering vector magnitude(s) in inverse Angstroms (1/Å).
    sld : float
        Parameter sld.
    sld_solvent : float
        Parameter sld_solvent.
    radius : float
        Parameter radius.
    fuzziness : float
        Parameter fuzziness.
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
            ctypes.c_double(sld),
            ctypes.c_double(sld_solvent),
            ctypes.c_double(radius),
            ctypes.c_double(fuzziness)
        )
        result[i] = f2.value  # Return intensity (F^2)
    
    return result
