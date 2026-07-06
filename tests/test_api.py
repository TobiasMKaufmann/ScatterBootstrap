"""Tests for the public API surface and model discovery."""

import numpy as np
import pytest

import scatterbootstrap as sb


def test_public_api_is_importable():
    for name in [
        "form_factor",
        "structure_factor",
        "intensity",
        "fit_data",
        "residuals_bootstrap",
        "fit_bootstrap_many",
        "compute_confidence_intervals",
        "plot_data",
        "plot_fit_data",
        "list_form_factor_models",
        "list_structure_factor_models",
    ]:
        assert hasattr(sb, name), f"missing public symbol: {name}"
        assert callable(getattr(sb, name))


def test_version_is_exposed():
    assert isinstance(sb.__version__, str)
    assert sb.__version__.count(".") >= 1


def test_model_discovery_lists_bundled_models():
    ffs = sb.list_form_factor_models()
    sfs = sb.list_structure_factor_models()
    assert "sphere" in ffs
    assert "hardsphere" in sfs
    assert len(ffs) >= 14
    assert len(sfs) >= 2
    # Sorted, no duplicates.
    assert ffs == sorted(ffs)
    assert len(ffs) == len(set(ffs))


def test_callables_survive_model_discovery():
    """Regression test: the ``form_factor``/``structure_factor`` callables must
    not be shadowed by the same-named sub-packages once model discovery imports
    them (this previously broke the entire public API)."""
    sb.list_form_factor_models()
    sb.list_structure_factor_models()
    assert callable(sb.form_factor)
    assert callable(sb.structure_factor)


def test_scalar_input_returns_float(q):
    val = sb.form_factor(0.1, "sphere", sld=4e-6, sld_solvent=1e-6, radius=50)
    assert isinstance(val, float)


def test_array_input_returns_array_of_same_shape(q):
    out = sb.form_factor(q, "sphere", sld=4e-6, sld_solvent=1e-6, radius=50)
    assert isinstance(out, np.ndarray)
    assert out.shape == q.shape


def test_unknown_form_factor_raises_helpful_error():
    with pytest.raises(ImportError) as exc:
        sb.form_factor(0.1, "not_a_real_model", radius=1)
    assert "not_a_real_model" in str(exc.value)
    assert "sphere" in str(exc.value)  # lists available models


def test_unknown_structure_factor_raises_helpful_error():
    with pytest.raises(ImportError) as exc:
        sb.structure_factor(0.1, "nope", radius_effective=1, volfraction=0.1)
    assert "nope" in str(exc.value)


def test_intensity_without_structure_factor_is_scale_F2_plus_background(q):
    scale, background = 2.0, 0.01
    params = dict(sld=4e-6, sld_solvent=1e-6, radius=50)
    F2 = sb.form_factor(q, "sphere", **params)
    I = sb.intensity(q, scale, background, "sphere", **params)
    np.testing.assert_allclose(I, scale * F2 + background, rtol=1e-12)


def test_intensity_with_structure_factor(q):
    scale, background = 1.0, 0.0
    ff = dict(sld=4e-6, sld_solvent=1e-6, radius=50)
    sf = dict(radius_effective=50, volfraction=0.2)
    F2 = sb.form_factor(q, "sphere", **ff)
    Sq = sb.structure_factor(q, "hardsphere", **sf)
    I = sb.intensity(q, scale, background, "sphere", "hardsphere", **ff, **sf)
    np.testing.assert_allclose(I, scale * F2 * Sq + background, rtol=1e-10)
