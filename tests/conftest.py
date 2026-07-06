"""Shared pytest fixtures for the ScatterBootstrap test suite.

The ``FORM_FACTOR_PARAMS`` / ``STRUCTURE_FACTOR_PARAMS`` dictionaries hold a
physically reasonable parameter set for every bundled model, so the tests can
exercise each compiled C extension without hand-writing a separate test per
model.
"""

import numpy as np
import pytest

# Representative parameters for every bundled form factor model.
FORM_FACTOR_PARAMS = {
    "sphere": dict(sld=4e-6, sld_solvent=1e-6, radius=50),
    "ellipsoid": dict(
        sld=4e-6, sld_solvent=1e-6, radius_polar=20, radius_equatorial=50
    ),
    "core_shell_cylinder": dict(
        core_sld=4e-6,
        shell_sld=2e-6,
        solvent_sld=1e-6,
        radius=20,
        thickness=5,
        length=100,
    ),
    "barbell": dict(sld=4e-6, solvent_sld=1e-6, radius_bell=20, radius=10, length=50),
    "core_multi_shell": dict(
        core_sld=4e-6,
        core_radius=20,
        solvent_sld=1e-6,
        n_shells=2,
        sld_array=[3e-6, 2e-6],
        thickness_array=[10, 10],
    ),
    "elliptical_cylinder": dict(
        radius_minor=20, r_ratio=1.5, length=100, sld=4e-6, solvent_sld=1e-6
    ),
    "fuzzy_sphere": dict(sld=4e-6, sld_solvent=1e-6, radius=50, fuzziness=5),
    "lamellar_hg": dict(
        length_tail=15, length_head=10, sld=0.4e-6, sld_head=2e-6, sld_solvent=6e-6
    ),
    "linear_pearls": dict(
        radius=80, edge_sep=350, fp_num_pearls=3, pearl_sld=1e-6, solvent_sld=6.3e-6
    ),
    "onion": dict(
        sld_core=1e-6,
        radius_core=20,
        sld_solvent=6e-6,
        n_shells=2,
        sld_in=[1e-6, 2e-6],
        sld_out=[2e-6, 3e-6],
        thickness=[10, 10],
        A=[0.1, 0.1],
    ),
    "polymer_micelle": dict(
        ndensity=8.94e15,
        v_core=62624,
        v_corona=61940,
        solvent_sld=6.4e-6,
        core_sld=0.34e-6,
        corona_sld=0.8e-6,
        radius_core=45,
        rg=20,
        d_penetration=1,
        n_aggreg=6,
    ),
    "pringle": dict(
        radius=60, thickness=10, alpha=0.001, beta=0.02, sld=1e-6, sld_solvent=6.3e-6
    ),
    "bcc_paracrystal": dict(
        dnn=220, d_factor=0.06, radius=40, sld=4e-6, solvent_sld=1e-6
    ),
    "fcc_paracrystal": dict(
        dnn=220, d_factor=0.06, radius=40, sld=4e-6, solvent_sld=1e-6
    ),
}

# Representative parameters for every bundled structure factor model.
STRUCTURE_FACTOR_PARAMS = {
    "hardsphere": dict(radius_effective=50, volfraction=0.2),
    "hayter_msa": dict(
        radius_effective=20.75,
        volfraction=0.0192,
        charge=19,
        temperature=318,
        saltconc=0.0,
        dielectconst=71.08,
    ),
}


@pytest.fixture
def q():
    """A representative q grid (inverse Angstroms)."""
    return np.linspace(0.01, 0.4, 25)
