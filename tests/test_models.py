"""Smoke tests that every bundled C-extension model loads and computes.

Each model is exercised through the public API with a representative parameter
set (see ``conftest.py``) over an array and a scalar ``q``.
"""

import importlib

import numpy as np
import pytest

import scatterbootstrap as sb
from conftest import FORM_FACTOR_PARAMS, STRUCTURE_FACTOR_PARAMS


@pytest.mark.parametrize("model", sorted(FORM_FACTOR_PARAMS))
def test_every_form_factor_has_test_params(model):
    # Guard against a model being added without a corresponding fixture.
    assert model in sb.list_form_factor_models()


def test_all_bundled_form_factors_are_covered():
    assert set(FORM_FACTOR_PARAMS) == set(sb.list_form_factor_models())


def test_all_bundled_structure_factors_are_covered():
    assert set(STRUCTURE_FACTOR_PARAMS) == set(sb.list_structure_factor_models())


@pytest.mark.parametrize("model", sorted(FORM_FACTOR_PARAMS))
def test_form_factor_returns_finite_nonnegative(q, model):
    out = sb.form_factor(q, model, **FORM_FACTOR_PARAMS[model])
    assert out.shape == q.shape
    assert np.all(np.isfinite(out)), f"{model} produced non-finite values"
    assert np.all(out >= 0), f"{model} produced negative |F(q)|^2"


@pytest.mark.parametrize("model", sorted(FORM_FACTOR_PARAMS))
def test_form_factor_scalar_matches_array(q, model):
    arr = sb.form_factor(q, model, **FORM_FACTOR_PARAMS[model])
    scalar = sb.form_factor(float(q[0]), model, **FORM_FACTOR_PARAMS[model])
    assert isinstance(scalar, float)
    np.testing.assert_allclose(scalar, arr[0], rtol=1e-10)


@pytest.mark.parametrize("model", sorted(STRUCTURE_FACTOR_PARAMS))
def test_structure_factor_returns_finite_positive(q, model):
    out = sb.structure_factor(q, model, **STRUCTURE_FACTOR_PARAMS[model])
    assert out.shape == q.shape
    assert np.all(np.isfinite(out)), f"{model} produced non-finite values"
    assert np.all(out > 0), f"{model} produced non-positive S(q)"


def test_wrapper_modules_expose_compute_function():
    for model in sb.list_form_factor_models():
        mod = importlib.import_module(f"scatterbootstrap.form_factors.{model}.wrapper")
        assert hasattr(mod, "compute_form_factor")
    for model in sb.list_structure_factor_models():
        mod = importlib.import_module(
            f"scatterbootstrap.structure_factors.{model}.wrapper"
        )
        assert hasattr(mod, "compute_structure_factor")
