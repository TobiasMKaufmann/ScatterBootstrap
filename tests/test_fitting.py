"""Tests for fitting, bootstrap resampling and confidence intervals."""

import numpy as np
import pytest

import scatterbootstrap as sb
from scatterbootstrap.core import _flatten_params, _unflatten_params


@pytest.fixture
def sphere_dataset():
    """A noisy sphere intensity curve with known ground-truth parameters."""
    rng = np.random.default_rng(0)
    q = np.linspace(0.005, 0.5, 120)
    true = {
        "scale": 1.0,
        "background": 0.001,
        "sld": 4e-6,
        "sld_solvent": 1e-6,
        "radius": 50.0,
    }
    I = sb.intensity(q, form_factor_model="sphere", **true)
    I_noisy = I + rng.normal(0, 0.02 * I.max(), size=I.shape)
    return q, I_noisy, true


def test_fit_recovers_known_radius(sphere_dataset):
    q, I_noisy, true = sphere_dataset
    init = {**true, "radius": 40.0}
    fit_params = {k: (k == "radius") for k in true}
    popt, pcov, order = sb.fit_data(
        q,
        I_noisy,
        form_factor_model="sphere",
        initial_params=init,
        fit_params=fit_params,
    )
    assert order == ["radius"]
    assert popt[0] == pytest.approx(50.0, abs=1.0)
    assert np.all(np.isfinite(pcov))


def test_fit_returns_nans_on_failure_without_raising():
    # An empty dataset makes curve_fit fail; fit_data should degrade gracefully.
    init = {
        "scale": 1.0,
        "background": 0.0,
        "sld": 4e-6,
        "sld_solvent": 1e-6,
        "radius": 50.0,
    }
    fit_params = {k: (k == "radius") for k in init}
    popt, pcov, order = sb.fit_data(
        np.array([]),
        np.array([]),
        form_factor_model="sphere",
        initial_params=init,
        fit_params=fit_params,
    )
    assert order == ["radius"]
    assert np.all(np.isnan(popt))


def test_fit_data_requires_params():
    with pytest.raises(ValueError):
        sb.fit_data(np.array([0.1]), np.array([1.0]), form_factor_model="sphere")


def test_bootstrap_confidence_interval_brackets_truth(sphere_dataset):
    q, I_noisy, true = sphere_dataset
    init = {**true, "radius": 40.0}
    fit_params = {k: (k == "radius") for k in true}
    popt, _, _ = sb.fit_data(
        q,
        I_noisy,
        form_factor_model="sphere",
        initial_params=init,
        fit_params=fit_params,
    )
    fitted = {**init, "radius": popt[0]}
    boot = sb.residuals_bootstrap(
        q,
        I_noisy,
        form_factor_model="sphere",
        all_params=fitted,
        fit_params=fit_params,
        n_iterations=80,
        rng=1,
    )
    assert len(boot) == 80
    ci = sb.compute_confidence_intervals(boot, confidence_level=0.95)
    lo, hi = ci["radius"]
    assert lo < hi
    assert lo <= 50.0 <= hi


def test_bootstrap_is_reproducible_with_seed(sphere_dataset):
    q, I_noisy, true = sphere_dataset
    fitted = {**true}
    fit_params = {k: (k == "radius") for k in true}
    kw = dict(
        form_factor_model="sphere",
        all_params=fitted,
        fit_params=fit_params,
        n_iterations=25,
    )
    a = sb.residuals_bootstrap(q, I_noisy, rng=123, **kw)
    b = sb.residuals_bootstrap(q, I_noisy, rng=123, **kw)
    assert [r["radius"] for r in a] == [r["radius"] for r in b]


def test_bootstrap_requires_params():
    with pytest.raises(ValueError):
        sb.residuals_bootstrap(
            np.array([0.1]), np.array([1.0]), form_factor_model="sphere"
        )


def test_parallel_bootstrap_matches_serial(sphere_dataset):
    """n_jobs must not change the result: parallel == serial for the same seed."""
    q, I_noisy, true = sphere_dataset
    fit_params = {k: (k == "radius") for k in true}
    kw = dict(
        form_factor_model="sphere",
        all_params=true,
        fit_params=fit_params,
        n_iterations=40,
        rng=2024,
    )
    serial = sb.residuals_bootstrap(q, I_noisy, n_jobs=1, **kw)
    parallel = sb.residuals_bootstrap(q, I_noisy, n_jobs=2, **kw)
    assert [r["radius"] for r in serial] == [r["radius"] for r in parallel]


def test_n_jobs_minus_one_runs(sphere_dataset):
    q, I_noisy, true = sphere_dataset
    fit_params = {k: (k == "radius") for k in true}
    res = sb.residuals_bootstrap(
        q,
        I_noisy,
        form_factor_model="sphere",
        all_params=true,
        fit_params=fit_params,
        n_iterations=16,
        rng=1,
        n_jobs=-1,
    )
    assert len(res) == 16


def test_resolve_n_jobs():
    from scatterbootstrap.core import _resolve_n_jobs

    assert _resolve_n_jobs(1, 100) == 1
    assert _resolve_n_jobs(None, 100) == 1
    assert _resolve_n_jobs(0, 100) == 1
    assert _resolve_n_jobs(4, 100) == 4
    assert _resolve_n_jobs(8, 5) == 5  # capped at n_iterations
    assert _resolve_n_jobs(-1, 100) >= 1  # all cores


# ---- batch fit + bootstrap over many datasets ----


@pytest.fixture
def many_sphere_datasets():
    """Several noisy sphere datasets with different known radii."""
    rng = np.random.default_rng(0)
    q = np.linspace(0.005, 0.5, 100)
    true_radii = {"A": 40.0, "B": 55.0, "C": 70.0}
    datasets = {}
    for name, radius in true_radii.items():
        p = {
            "scale": 1.0,
            "background": 0.001,
            "sld": 4e-6,
            "sld_solvent": 1e-6,
            "radius": radius,
        }
        I = sb.intensity(q, form_factor_model="sphere", **p)
        datasets[name] = (q, I + rng.normal(0, 0.02 * I.max(), size=I.shape))
    return datasets, true_radii


def _batch_kwargs():
    init = {
        "scale": 1.0,
        "background": 0.001,
        "sld": 4e-6,
        "sld_solvent": 1e-6,
        "radius": 50.0,
    }
    fitp = {k: (k == "radius") for k in init}
    return dict(
        form_factor_model="sphere",
        initial_params=init,
        fit_params=fitp,
        n_iterations=40,
        rng=7,
    )


def test_fit_bootstrap_many_recovers_each_dataset(many_sphere_datasets):
    datasets, true_radii = many_sphere_datasets
    results = sb.fit_bootstrap_many(datasets, n_jobs=-1, **_batch_kwargs())
    assert set(results) == set(datasets)
    for name, radius in true_radii.items():
        r = results[name]
        assert r["fitted_params"]["radius"] == pytest.approx(radius, abs=2.0)
        lo, hi = r["confidence_intervals"]["radius"]
        assert lo <= radius <= hi
        assert len(r["bootstrap"]) == 40


def test_fit_bootstrap_many_parallel_matches_serial(many_sphere_datasets):
    datasets, _ = many_sphere_datasets
    serial = sb.fit_bootstrap_many(datasets, n_jobs=1, **_batch_kwargs())
    parallel = sb.fit_bootstrap_many(datasets, n_jobs=2, **_batch_kwargs())
    for name in datasets:
        assert [d["radius"] for d in serial[name]["bootstrap"]] == [
            d["radius"] for d in parallel[name]["bootstrap"]
        ]


def test_fit_bootstrap_many_single_dataset(many_sphere_datasets):
    datasets, true_radii = many_sphere_datasets
    one = {"A": datasets["A"]}
    results = sb.fit_bootstrap_many(one, n_jobs=-1, **_batch_kwargs())
    assert set(results) == {"A"}
    assert results["A"]["fitted_params"]["radius"] == pytest.approx(
        true_radii["A"], abs=2.0
    )


def test_fit_bootstrap_many_per_dataset_initial_params(many_sphere_datasets):
    datasets, _ = many_sphere_datasets
    base = _batch_kwargs()
    shared_init = base.pop("initial_params")
    fitp = base.pop("fit_params")
    per_init = {name: dict(shared_init) for name in datasets}
    per_init["A"]["radius"] = 38.0  # different start for one dataset
    results = sb.fit_bootstrap_many(
        datasets, initial_params=per_init, fit_params=fitp, **base
    )
    assert set(results) == set(datasets)


def test_fit_bootstrap_many_keep_ensembles_false(many_sphere_datasets):
    datasets, _ = many_sphere_datasets
    results = sb.fit_bootstrap_many(
        datasets, n_jobs=1, keep_ensembles=False, **_batch_kwargs()
    )
    for name in datasets:
        assert results[name]["bootstrap"] is None
        assert "radius" in results[name]["confidence_intervals"]


def test_fit_bootstrap_many_requires_params():
    with pytest.raises(ValueError):
        sb.fit_bootstrap_many(
            {"A": (np.array([0.1]), np.array([1.0]))}, form_factor_model="sphere"
        )


def test_fit_bootstrap_many_empty():
    assert (
        sb.fit_bootstrap_many(
            {}, form_factor_model="sphere", initial_params={}, fit_params={}
        )
        == {}
    )


# ---- parameter flattening (list-valued params used by onion / core_multi_shell) ----


def test_flatten_unflatten_roundtrip():
    initial = {"scale": 1.0, "thickness": [10.0, 20.0, 30.0]}
    fit = {"scale": True, "thickness": [True, False, True]}
    flat_initial, flat_fit, groups = _flatten_params(initial, fit)
    assert flat_initial == {
        "scale": 1.0,
        "thickness_0": 10.0,
        "thickness_1": 20.0,
        "thickness_2": 30.0,
    }
    assert flat_fit == {
        "scale": True,
        "thickness_0": True,
        "thickness_1": False,
        "thickness_2": True,
    }
    regrouped = _unflatten_params(flat_initial, groups)
    assert regrouped == {"scale": 1.0, "thickness": [10.0, 20.0, 30.0]}


def test_flatten_scalar_fit_flag_broadcasts_over_list():
    initial = {"sld": [1.0, 2.0]}
    fit = {"sld": True}
    _, flat_fit, _ = _flatten_params(initial, fit)
    assert flat_fit == {"sld_0": True, "sld_1": True}


def test_confidence_interval_widens_with_level():
    rng = np.random.default_rng(0)
    samples = [{"x": v} for v in rng.normal(0, 1, size=2000)]
    ci90 = sb.compute_confidence_intervals(samples, 0.90)["x"]
    ci99 = sb.compute_confidence_intervals(samples, 0.99)["x"]
    assert ci99[0] <= ci90[0]
    assert ci99[1] >= ci90[1]
