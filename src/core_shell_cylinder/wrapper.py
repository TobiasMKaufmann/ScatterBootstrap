from ctypes import CDLL, c_double, POINTER
import os
from pathlib import Path

lib_path = os.path.join(os.path.dirname(__file__), 'core_shell_cylinder.so')
core_shell_lib = CDLL(lib_path)

def compute_form_factor(q, core_sld, shell_sld, solvent_sld, radius, thickness, length):
    """
    Compute the form factor for the core-shell cylinder model.

    Parameters:
    q (float): The scattering vector magnitude.
    core_sld (float): The scattering length density of the core.
    shell_sld (float): The scattering length density of the shell.
    solvent_sld (float): The scattering length density of the solvent.
    radius (float): The radius of the core.
    thickness (float): The thickness of the shell.
    length (float): The length of the cylinder.

    Returns:
    float: The computed form factor.
    """
    F1 = c_double()
    F2 = c_double()

    core_shell_lib.Fq(
        c_double(q),
        POINTER(c_double)(F1),
        POINTER(c_double)(F2),
        c_double(core_sld),
        c_double(shell_sld),
        c_double(solvent_sld),
        c_double(radius),
        c_double(thickness),
        c_double(length)
    )

    return F1.value, F2.value