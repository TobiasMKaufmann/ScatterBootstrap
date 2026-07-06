"""
Core analysis utilities for Small-Angle Scattering (SAS).

This module is the main analysis API of the ScatterBootstrap package, providing
tools for computing scattering intensities, fitting experimental data, and
quantifying parameter uncertainties via residuals bootstrapping.

Models are selected by name (matching the subdirectories of
``scatterbootstrap.form_factors`` and ``scatterbootstrap.structure_factors``) and
passed explicitly to the functions below -- nothing needs to be edited in this
module to switch models. Use :func:`list_form_factor_models` and
:func:`list_structure_factor_models` to discover the available model names.

Functions Overview
===================
- :func:`form_factor`, :func:`structure_factor`, :func:`intensity` -- core
  scattering calculations
- :func:`fit_data` -- non-linear least squares fitting via
  ``scipy.optimize.curve_fit``
- :func:`residuals_bootstrap` -- uncertainty analysis via bootstrap resampling
  (parallelizable with ``n_jobs``)
- :func:`fit_bootstrap_many` -- batch fit + bootstrap over many datasets in
  parallel
- :func:`compute_confidence_intervals` -- percentile confidence intervals from
  bootstrap results
- :func:`plot_data`, :func:`plot_fit_data` -- simple plotting helpers

Example
-------
    from scatterbootstrap import form_factor, intensity, fit_data

    F2 = form_factor(0.05, "sphere", sld=4e-6, sld_solvent=1e-6, radius=50)

    fitted_params, covariance, param_order = fit_data(
        q_data, I_data,
        form_factor_model="sphere",
        initial_params={"scale": 1, "background": 0.001, "sld": 4e-6,
                         "sld_solvent": 1e-6, "radius": 50},
        fit_params={"scale": True, "background": True, "sld": False,
                    "sld_solvent": False, "radius": True},
    )
"""

import importlib
import os
import pkgutil
from concurrent.futures import ProcessPoolExecutor

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from tqdm import tqdm
from scipy.optimize import curve_fit

# ==================== MODEL DISCOVERY ====================


def list_form_factor_models():
    """Return the names of all available form factor models."""
    package = importlib.import_module(f"{__package__}.form_factors")
    return sorted(
        name for _, name, is_pkg in pkgutil.iter_modules(package.__path__) if is_pkg
    )


def list_structure_factor_models():
    """Return the names of all available structure factor models."""
    package = importlib.import_module(f"{__package__}.structure_factors")
    return sorted(
        name for _, name, is_pkg in pkgutil.iter_modules(package.__path__) if is_pkg
    )


def _load_form_factor(model):
    try:
        return importlib.import_module(f"{__package__}.form_factors.{model}.wrapper")
    except ImportError as e:
        raise ImportError(
            f"Unknown form factor model '{model}'. "
            f"Available models: {', '.join(list_form_factor_models())}."
        ) from e


def _load_structure_factor(model):
    try:
        return importlib.import_module(
            f"{__package__}.structure_factors.{model}.wrapper"
        )
    except ImportError as e:
        raise ImportError(
            f"Unknown structure factor model '{model}'. "
            f"Available models: {', '.join(list_structure_factor_models())}."
        ) from e


def _match_input_shape(q, result):
    """Return a Python float if q was a scalar, otherwise the array unchanged."""
    result = np.asarray(result)
    if np.ndim(q) == 0:
        return float(result.reshape(-1)[0])
    return result


# ==================== SCATTERING CALCULATIONS ====================


def form_factor(q, model, **params):
    """
    Compute the form factor squared, F^2(q), for the given model.

    Parameters
    ----------
    q : float or array_like
        Scattering vector magnitude(s) in inverse Angstroms (1/A).
    model : str
        Name of the form factor model (see :func:`list_form_factor_models`).
    **params : dict
        Model-specific parameters, see the model's
        ``scatterbootstrap.form_factors.<model>.wrapper.compute_form_factor``
        for the expected keyword arguments.

    Returns
    -------
    float or ndarray
        F^2(q). A float is returned if `q` was scalar, otherwise an array
        with the same shape as `q`.
    """
    module = _load_form_factor(model)
    result = module.compute_form_factor(np.asarray(q, dtype=float), **params)
    return _match_input_shape(q, result)


def structure_factor(q, model, **params):
    """
    Compute the structure factor S(q) for the given model.

    Parameters
    ----------
    q : float or array_like
        Scattering vector magnitude(s) in inverse Angstroms (1/A).
    model : str
        Name of the structure factor model (see :func:`list_structure_factor_models`).
    **params : dict
        Model-specific parameters, see the model's
        ``scatterbootstrap.structure_factors.<model>.wrapper.compute_structure_factor``
        for the expected keyword arguments.

    Returns
    -------
    float or ndarray
        S(q). A float is returned if `q` was scalar, otherwise an array
        with the same shape as `q`.
    """
    module = _load_structure_factor(model)
    result = module.compute_structure_factor(np.asarray(q, dtype=float), **params)
    return _match_input_shape(q, result)


def intensity(
    q, scale, background, form_factor_model, structure_factor_model=None, **params
):
    """
    Compute the total scattering intensity I(q) = scale * F^2(q) * S(q) + background.

    Parameters
    ----------
    q : float or array_like
        Scattering vector magnitude(s) in inverse Angstroms (1/A).
    scale : float
        Overall scale factor.
    background : float
        Flat background intensity.
    form_factor_model : str
        Name of the form factor model (see :func:`list_form_factor_models`).
    structure_factor_model : str, optional
        Name of the structure factor model (see :func:`list_structure_factor_models`).
        If None (default), S(q) = 1 (form-factor-only intensity).
    **params : dict
        Combined model-specific parameters for the chosen form factor and,
        if applicable, structure factor model.

    Returns
    -------
    float or ndarray
        I(q). A float is returned if `q` was scalar, otherwise an array
        with the same shape as `q`.
    """
    q_arr = np.asarray(q, dtype=float)

    F2 = _load_form_factor(form_factor_model).compute_form_factor(q_arr, **params)

    if structure_factor_model is not None:
        S_q = _load_structure_factor(structure_factor_model).compute_structure_factor(
            q_arr, **params
        )
    else:
        S_q = 1.0

    result = scale * F2 * S_q + background
    return _match_input_shape(q, result)


# ==================== PARAMETER FLATTENING (for list-valued parameters) ====================


def _flatten_params(initial_params, fit_params):
    """
    Flatten list/array-valued parameters (e.g. the ``thickness``/``sld_in``/``sld_out``
    arrays of the onion and core_multi_shell models) into individually-named scalar
    entries (``name_0``, ``name_1``, ...) suitable for ``curve_fit``.

    Returns
    -------
    flat_initial : dict
        Flat parameter name -> scalar initial value.
    flat_fit : dict
        Flat parameter name -> bool, whether to fit this scalar.
    groups : dict
        Flat parameter name -> (original_name, index) for entries that came
        from a list/array, or None for entries that were already scalar.
    """
    flat_initial = {}
    flat_fit = {}
    groups = {}

    for name, value in initial_params.items():
        fit_flag = fit_params.get(name, False)
        if isinstance(value, (list, tuple, np.ndarray)):
            for i, v in enumerate(value):
                flat_name = f"{name}_{i}"
                flat_initial[flat_name] = v
                flat_fit[flat_name] = (
                    fit_flag[i]
                    if isinstance(fit_flag, (list, tuple, np.ndarray))
                    else fit_flag
                )
                groups[flat_name] = (name, i)
        else:
            flat_initial[name] = value
            flat_fit[name] = fit_flag
            groups[name] = None

    return flat_initial, flat_fit, groups


def _unflatten_params(values, groups):
    """Inverse of :func:`_flatten_params`: regroup ``name_0``, ``name_1``, ... back into lists."""
    grouped = {}
    list_groups = {}
    for flat_name, val in values.items():
        group = groups[flat_name]
        if group is None:
            grouped[flat_name] = val
        else:
            base, idx = group
            list_groups.setdefault(base, {})[idx] = val
    for base, idx_map in list_groups.items():
        grouped[base] = [idx_map[i] for i in sorted(idx_map)]
    return grouped


# ==================== FITTING ====================


def fit_data(
    x_data,
    y_data,
    form_factor_model,
    structure_factor_model=None,
    initial_params=None,
    fit_params=None,
    bounds=(-np.inf, np.inf),
    method="lm",
    maxfev=2000,
):
    """
    Fit experimental data to a scattering model using non-linear least squares.

    Parameters
    ----------
    x_data : array_like
        Independent variable data (scattering vector q).
    y_data : array_like
        Dependent variable data (intensity I).
    form_factor_model : str
        Name of the form factor model (see :func:`list_form_factor_models`).
    structure_factor_model : str, optional
        Name of the structure factor model (see :func:`list_structure_factor_models`).
        If None (default), S(q) = 1 (form-factor-only fit).
    initial_params : dict
        Initial values for every parameter required by the chosen models
        (including ``scale`` and ``background``). List/array-valued entries
        are supported for models such as onion and core_multi_shell.
    fit_params : dict
        Same keys as `initial_params`, mapping each to True (fit this
        parameter) or False (keep it fixed at its initial value). For
        list-valued parameters, this may itself be a list of booleans.
    bounds : tuple of array_like or dict, optional
        Lower and upper bounds for the fitted parameters. Either a 2-tuple
        of arrays (as accepted by ``scipy.optimize.curve_fit``) or a dict
        mapping parameter names to ``(lower, upper)`` tuples (or, for
        list-valued parameters, a list of such tuples).
        Default is ``(-np.inf, np.inf)``.
    method : str, optional
        Fitting method for ``scipy.optimize.curve_fit``: 'lm'
        (Levenberg-Marquardt), 'trf' (Trust Region Reflective), or 'dogbox'.
        Default is 'lm'.
    maxfev : int, optional
        Maximum number of function evaluations. Default is 2000.

    Returns
    -------
    popt : ndarray
        Optimal values for the fitted parameters, in the order given by
        `param_order`. If fitting fails, this is filled with NaN.
    pcov : ndarray
        Covariance matrix of `popt`. If fitting fails, this is filled with NaN.
    param_order : list of str
        Names of the fitted parameters, in the order they appear in `popt`
        (list-valued parameters appear as ``name_0``, ``name_1``, ...).
    """
    if initial_params is None or fit_params is None:
        raise ValueError("initial_params and fit_params must be provided")

    x_data = np.asarray(x_data, dtype=float)
    y_data = np.asarray(y_data, dtype=float)

    flat_initial, flat_fit, groups = _flatten_params(initial_params, fit_params)

    param_order = [name for name, fit in flat_fit.items() if fit]
    fixed_values = {
        name: val for name, val in flat_initial.items() if not flat_fit[name]
    }

    if isinstance(bounds, dict):
        lower_bounds, upper_bounds = [], []
        for name in param_order:
            group = groups[name]
            param_bounds = bounds[name] if group is None else bounds[group[0]][group[1]]
            lower_bounds.append(param_bounds[0])
            upper_bounds.append(param_bounds[1])
        bounds = (lower_bounds, upper_bounds)

    def f(q, *fitting):
        values = dict(zip(param_order, fitting))
        values.update(fixed_values)
        params = _unflatten_params(values, groups)
        return intensity(
            q,
            form_factor_model=form_factor_model,
            structure_factor_model=structure_factor_model,
            **params,
        )

    p0 = [flat_initial[name] for name in param_order]

    try:
        popt, pcov = curve_fit(
            f, x_data, y_data, p0=p0, bounds=bounds, method=method, maxfev=maxfev
        )
    except Exception as e:
        print(f"Error during curve fitting: {e}\nMoving on to next one.")
        n = len(param_order)
        return np.full(n, np.nan), np.full((n, n), np.nan), param_order

    return popt, pcov, param_order


# ==================== PLOTTING ====================


def plot_data(xdata, ydata, title="Data Plot", xlabel="q", ylabel="Intensity"):
    """
    Plot experimental data points and save to ``<title>.png``.

    Parameters
    ----------
    xdata, ydata : array_like
        Independent and dependent variable data.
    title, xlabel, ylabel : str, optional
        Plot title and axis labels. The title (lowercased, spaces replaced
        with underscores) is used as the output filename.
    """
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.scatter(xdata, ydata, label="Data", color="blue", s=10)

    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.legend()
    ax.grid(True)

    plt.savefig(f"{title.replace(' ', '_').lower()}.png", dpi=300)
    plt.close(fig)


def plot_fit_data(
    xdata,
    ydata,
    params,
    form_factor_model,
    structure_factor_model=None,
    title="Fit Data",
    xlabel="q",
    ylabel="Intensity",
    folder=None,
):
    """
    Plot experimental data together with the fitted model curve.

    Parameters
    ----------
    xdata, ydata : array_like
        Independent and dependent variable data.
    params : dict
        Parameters for :func:`intensity` (including ``scale`` and ``background``).
    form_factor_model : str
        Name of the form factor model (see :func:`list_form_factor_models`).
    structure_factor_model : str, optional
        Name of the structure factor model. If None (default), S(q) = 1.
    title, xlabel, ylabel : str, optional
        Plot title and axis labels.
    folder : str, optional
        Folder to save the plot in. Defaults to the current working directory.
    """
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.scatter(xdata, ydata, label="Data", color="blue", s=10)

    fitted_y = intensity(
        xdata,
        form_factor_model=form_factor_model,
        structure_factor_model=structure_factor_model,
        **params,
    )

    ax.loglog(xdata, fitted_y, label="Fitted Curve", color="red")

    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.legend()
    ax.grid(True)

    if not folder:
        folder = os.getcwd()
    plt.savefig(os.path.join(folder, f"{title.replace(' ', '_').lower()}.png"), dpi=300)
    plt.close(fig)


# ==================== BOOTSTRAP UNCERTAINTY ANALYSIS ====================

# Per-process worker state, populated once per process by ``_bootstrap_init``.
# Using a module global (rather than a closure) keeps the per-task payload tiny
# -- only an integer seed is shipped to each task -- and keeps the worker
# function importable/picklable, which ``ProcessPoolExecutor`` requires.
_BOOTSTRAP_CTX = {}


def _resolve_n_jobs(n_jobs, n_iterations):
    """Translate a user-supplied ``n_jobs`` into an actual worker count.

    ``None``/``0``/``1`` -> serial; negative -> all available CPUs; otherwise the
    requested count. The result is capped at ``n_iterations``.
    """
    if not n_jobs or n_jobs == 1:
        return 1
    if n_jobs < 0:
        n_jobs = os.cpu_count() or 1
    return max(1, min(n_jobs, n_iterations))


def _bootstrap_one(seed, context):
    """Run one bootstrap iteration: resample residuals, build a synthetic
    dataset, refit it, and return the refitted parameters.

    Returns ``(synthetic_y_or_None, fitted_values)``. ``synthetic_y`` is only
    returned when an HDF5 store is in use (``context["store_synthetic"]``), to
    avoid shipping large arrays back from worker processes unnecessarily.
    """
    local_rng = np.random.default_rng(seed)
    residuals = context["residuals"]
    resampled = local_rng.choice(residuals, size=len(residuals), replace=True)
    synthetic_y = context["y_data"] + resampled

    popt, _, param_order = fit_data(
        context["x_data"],
        synthetic_y,
        context["form_factor_model"],
        context["structure_factor_model"],
        initial_params=context["all_params"],
        fit_params=context["fit_params"],
        bounds=context["bounds"],
        method=context["method"],
    )
    fitted_values = dict(zip(param_order, popt))
    return (synthetic_y if context["store_synthetic"] else None), fitted_values


def _bootstrap_init(context):
    """ProcessPoolExecutor initializer: cache the shared context per worker."""
    _BOOTSTRAP_CTX.clear()
    _BOOTSTRAP_CTX.update(context)


def _bootstrap_worker(seed):
    """ProcessPoolExecutor task: run one iteration using the cached context."""
    return _bootstrap_one(seed, _BOOTSTRAP_CTX)


def _collect_bootstrap(results, n_iterations, flat_all, groups, store, desc):
    """Consume bootstrap results (in order), optionally writing to ``store``."""
    fit_arr = []
    for i, (synthetic_y, fitted_values) in enumerate(
        tqdm(results, total=n_iterations, desc=desc, unit="iteration")
    ):
        if store is not None:
            if synthetic_y is not None:
                store.put(f"synthetic_y/s{i}", pd.Series(synthetic_y))
            store.put(f"fitted_params/s{i}", pd.Series(fitted_values))

        merged = dict(fitted_values)
        for name, value in flat_all.items():
            merged.setdefault(name, value)
        fit_arr.append(_unflatten_params(merged, groups))
    return fit_arr


def residuals_bootstrap(
    x_data,
    y_data,
    form_factor_model,
    structure_factor_model=None,
    all_params=None,
    fit_params=None,
    n_iterations=1000,
    bounds=(-np.inf, np.inf),
    store=None,
    method="lm",
    rng=None,
    n_jobs=1,
):
    """
    Perform residuals bootstrap resampling to quantify parameter uncertainties.

    Resamples residuals from the fit given by `all_params`, creates synthetic
    datasets, refits each one, and returns the resulting parameter sets for
    use with :func:`compute_confidence_intervals`.

    Parameters
    ----------
    x_data, y_data : array_like
        Independent and dependent variable data (q and I).
    form_factor_model : str
        Name of the form factor model (see :func:`list_form_factor_models`).
    structure_factor_model : str, optional
        Name of the structure factor model. If None (default), S(q) = 1.
    all_params : dict
        Parameter values from the original fit (same structure as
        `initial_params` in :func:`fit_data`).
    fit_params : dict
        Same keys as `all_params`, mapping each to True (refit this
        parameter for every bootstrap sample) or False (keep it fixed).
    n_iterations : int, optional
        Number of bootstrap iterations. Default is 1000.
    bounds : tuple of array_like or dict, optional
        Bounds passed through to :func:`fit_data`. Default is ``(-np.inf, np.inf)``.
    store : pd.HDFStore, optional
        If provided, the residuals, synthetic datasets, and per-iteration
        fitted parameters are written to this HDF5 store.
    method : str, optional
        Fitting method passed through to :func:`fit_data`. Default is "lm".
    rng : int, numpy.random.Generator, or None, optional
        Seed or generator used for resampling, passed to
        ``numpy.random.default_rng``. Default is None (fresh, unseeded
        generator). Each iteration draws from its own independent child
        seed, so results are reproducible **and identical regardless of**
        `n_jobs`.
    n_jobs : int, optional
        Number of worker processes used to run the independent refits in
        parallel. ``1`` (default) runs serially; ``-1`` uses all available
        CPU cores; any other positive integer uses that many processes.
        Because each bootstrap refit is independent, this gives a near-linear
        speedup on multi-core machines and clusters. Parallelism uses
        processes (not threads), since the fitting holds the GIL.

    Returns
    -------
    list of dict
        One parameter dictionary per bootstrap iteration, with the same
        structure as `all_params`.

    Notes
    -----
    On the cluster, set ``n_jobs`` to the number of allocated cores (e.g.
    SLURM's ``$SLURM_CPUS_PER_TASK``) to actually use them.

    When ``n_jobs != 1`` on macOS or Windows (which use the "spawn" start
    method), the calling code must be guarded by ``if __name__ == "__main__":``,
    as required by ``multiprocessing``. On Linux ("fork") this is not needed.
    """
    if all_params is None or fit_params is None:
        raise ValueError("all_params and fit_params must be provided")

    x_data = np.asarray(x_data, dtype=float)
    y_data = np.asarray(y_data, dtype=float)

    rng = np.random.default_rng(rng)

    fitted_y = intensity(
        x_data,
        form_factor_model=form_factor_model,
        structure_factor_model=structure_factor_model,
        **all_params,
    )
    residuals = y_data - fitted_y

    if store is not None:
        store.put("residuals", pd.Series(residuals))

    flat_all, _, groups = _flatten_params(all_params, fit_params)

    # One independent child seed per iteration, derived up front so the results
    # are deterministic and do not depend on how the work is split across
    # processes.
    master_seed = int(rng.integers(0, 2**63 - 1))
    child_seeds = np.random.SeedSequence(master_seed).spawn(n_iterations)

    context = {
        "x_data": x_data,
        "y_data": y_data,
        "residuals": residuals,
        "form_factor_model": form_factor_model,
        "structure_factor_model": structure_factor_model,
        "all_params": all_params,
        "fit_params": fit_params,
        "bounds": bounds,
        "method": method,
        "store_synthetic": store is not None,
    }

    n_workers = _resolve_n_jobs(n_jobs, n_iterations)

    if n_workers == 1:
        results = (_bootstrap_one(seed, context) for seed in child_seeds)
        return _collect_bootstrap(
            results, n_iterations, flat_all, groups, store, "Bootstrapping residuals"
        )

    chunksize = max(1, n_iterations // (n_workers * 4))
    with ProcessPoolExecutor(
        max_workers=n_workers, initializer=_bootstrap_init, initargs=(context,)
    ) as executor:
        results = executor.map(_bootstrap_worker, child_seeds, chunksize=chunksize)
        return _collect_bootstrap(
            results,
            n_iterations,
            flat_all,
            groups,
            store,
            f"Bootstrapping residuals (n_jobs={n_workers})",
        )


def compute_confidence_intervals(fitted_params, confidence_level=0.95):
    """
    Compute confidence intervals from bootstrap parameter distributions.

    Calculates percentile-based confidence intervals from bootstrap samples:
    for a given `confidence_level` (e.g. 0.95 for a 95% CI), the interval
    spans the [alpha/2, 1 - alpha/2] percentiles, where alpha = 1 - confidence_level.

    Parameters
    ----------
    fitted_params : list of dict
        List of parameter dictionaries from bootstrap samples (e.g. the
        output of :func:`residuals_bootstrap`). Each dictionary must have
        the same scalar-valued keys.
    confidence_level : float, optional
        Desired confidence level, e.g. 0.95 for a 95% confidence interval.
        Default is 0.95.

    Returns
    -------
    dict
        Dictionary mapping parameter names to ``(lower_bound, upper_bound)``
        tuples, computed using ``numpy.percentile`` with ``method="nearest"``.
    """
    dict_of_lists = {
        key: np.array([d[key] for d in fitted_params])
        for key in fitted_params[0].keys()
    }

    param_order = list(dict_of_lists.keys())
    arr_fitted_params = np.array([dict_of_lists[key] for key in param_order]).T

    alpha = 1.0 - confidence_level
    lower_bound = np.percentile(
        arr_fitted_params, (alpha / 2) * 100, method="nearest", axis=0
    )
    upper_bound = np.percentile(
        arr_fitted_params, (1 - alpha / 2) * 100, method="nearest", axis=0
    )

    return {
        param_order[i]: (lower_bound[i], upper_bound[i])
        for i in range(len(param_order))
    }


# ==================== BATCH FIT + BOOTSTRAP (many datasets) ====================


def _fit_and_bootstrap_one(task):
    """Fit one dataset and bootstrap it. Top-level so it is picklable for
    ``ProcessPoolExecutor``. ``task`` is a fully self-contained tuple."""
    (
        name,
        x_data,
        y_data,
        form_factor_model,
        structure_factor_model,
        initial_params,
        fit_params,
        bounds,
        method,
        n_iterations,
        confidence_level,
        seed,
        bootstrap_n_jobs,
        keep_ensemble,
    ) = task

    x_data = np.asarray(x_data, dtype=float)
    y_data = np.asarray(y_data, dtype=float)

    popt, pcov, param_order = fit_data(
        x_data,
        y_data,
        form_factor_model,
        structure_factor_model,
        initial_params=initial_params,
        fit_params=fit_params,
        bounds=bounds,
        method=method,
    )

    # Reconstruct the full (unflattened) parameter dict with fitted values, so it
    # can seed the bootstrap. Handles list-valued parameters transparently.
    flat_initial, _, groups = _flatten_params(initial_params, fit_params)
    fitted_flat = dict(flat_initial)
    fitted_flat.update(dict(zip(param_order, popt)))
    fitted_params = _unflatten_params(fitted_flat, groups)

    if np.all(np.isnan(popt)):
        # Initial fit failed; skip the (meaningless) bootstrap but don't crash
        # the whole batch.
        return name, {
            "fitted_params": fitted_params,
            "param_order": param_order,
            "covariance": pcov,
            "confidence_intervals": {},
            "bootstrap": [] if keep_ensemble else None,
            "error": "initial fit failed",
        }

    ensemble = residuals_bootstrap(
        x_data,
        y_data,
        form_factor_model,
        structure_factor_model,
        all_params=fitted_params,
        fit_params=fit_params,
        n_iterations=n_iterations,
        bounds=bounds,
        method=method,
        rng=seed,
        n_jobs=bootstrap_n_jobs,
    )
    confidence_intervals = compute_confidence_intervals(ensemble, confidence_level)

    return name, {
        "fitted_params": fitted_params,
        "param_order": param_order,
        "covariance": pcov,
        "confidence_intervals": confidence_intervals,
        "bootstrap": ensemble if keep_ensemble else None,
    }


def fit_bootstrap_many(
    datasets,
    form_factor_model,
    structure_factor_model=None,
    initial_params=None,
    fit_params=None,
    bounds=(-np.inf, np.inf),
    n_iterations=1000,
    method="lm",
    confidence_level=0.95,
    rng=None,
    n_jobs=-1,
    bootstrap_n_jobs=None,
    keep_ensembles=True,
):
    """Fit *and* bootstrap many datasets, in parallel.

    This is the batch entry point: it runs the full
    :func:`fit_data` -> :func:`residuals_bootstrap` ->
    :func:`compute_confidence_intervals` pipeline for each dataset and
    distributes the work across CPU cores. It is reproducible: a given `rng`
    seed yields the same results regardless of `n_jobs`.

    Parameters
    ----------
    datasets : dict
        Mapping ``name -> (q, I)`` where ``q`` and ``I`` are array_like. The
        names are used as the keys of the returned dictionary.
    form_factor_model : str
        Name of the form factor model (see :func:`list_form_factor_models`).
    structure_factor_model : str, optional
        Name of the structure factor model. If None (default), S(q) = 1.
    initial_params : dict or dict of dict
        Either one parameter dictionary applied to every dataset, or a mapping
        ``name -> initial_params`` for per-dataset starting values.
    fit_params : dict or dict of dict
        Either one fit-flag dictionary applied to every dataset, or a mapping
        ``name -> fit_params``.
    bounds : tuple, dict, or dict of those, optional
        Bounds passed to :func:`fit_data`. May be given per dataset as a
        mapping ``name -> bounds``. Default is ``(-np.inf, np.inf)``.
    n_iterations : int, optional
        Bootstrap iterations per dataset. Default is 1000.
    method : str, optional
        Fitting method passed to :func:`fit_data`. Default is "lm".
    confidence_level : float, optional
        Confidence level for the per-dataset intervals. Default is 0.95.
    rng : int, numpy.random.Generator, or None, optional
        Master seed. Each dataset gets its own independent child seed derived
        from it, so results are reproducible and independent of `n_jobs`.
    n_jobs : int, optional
        Parallelism **across datasets**: ``1`` serial, ``-1`` (default) all
        cores, or an explicit count.
    bootstrap_n_jobs : int or None, optional
        Parallelism **within** each dataset's bootstrap. By default (None) this
        is budgeted automatically to avoid oversubscription: when several
        datasets run concurrently each bootstrap runs serially; when datasets
        run one at a time (``n_jobs=1`` or a single dataset) the bootstrap uses
        all cores. Set explicitly only if you know what you are doing.
    keep_ensembles : bool, optional
        If True (default), the full bootstrap ensemble is returned for each
        dataset under the ``"bootstrap"`` key. Set False to keep only the
        confidence intervals (saves memory for large batches).

    Returns
    -------
    dict
        Mapping ``name -> result`` where each ``result`` is a dict with keys
        ``"fitted_params"`` (full parameter dict), ``"param_order"``,
        ``"covariance"``, ``"confidence_intervals"``, and (if
        `keep_ensembles`) ``"bootstrap"``. Datasets whose initial fit failed
        additionally carry an ``"error"`` key.

    Notes
    -----
    On macOS/Windows (spawn start method), call this from within an
    ``if __name__ == "__main__":`` guard, as required by ``multiprocessing``.
    """
    if initial_params is None or fit_params is None:
        raise ValueError("initial_params and fit_params must be provided")

    items = list(datasets.items())
    n_datasets = len(items)
    if n_datasets == 0:
        return {}

    def _per_dataset(value, name):
        # Allow a single shared config or a per-dataset mapping keyed by name.
        if isinstance(value, dict) and name in value and isinstance(value[name], dict):
            return value[name]
        return value

    dataset_workers = _resolve_n_jobs(n_jobs, n_datasets)

    # Budget cores between the two levels so we never oversubscribe or nest pools.
    if bootstrap_n_jobs is None:
        inner_jobs = 1 if dataset_workers > 1 else -1
    else:
        inner_jobs = bootstrap_n_jobs

    # One independent, order-independent seed per dataset.
    master_seed = int(np.random.default_rng(rng).integers(0, 2**63 - 1))
    seeds = np.random.SeedSequence(master_seed).spawn(n_datasets)

    tasks = []
    for (name, (q, intensity_data)), seed in zip(items, seeds):
        tasks.append(
            (
                name,
                q,
                intensity_data,
                form_factor_model,
                structure_factor_model,
                _per_dataset(initial_params, name),
                _per_dataset(fit_params, name),
                _per_dataset(bounds, name) if isinstance(bounds, dict) else bounds,
                method,
                n_iterations,
                confidence_level,
                seed,
                inner_jobs,
                keep_ensembles,
            )
        )

    results = {}
    if dataset_workers == 1:
        for task in tqdm(tasks, desc="Datasets", unit="dataset"):
            name, result = _fit_and_bootstrap_one(task)
            results[name] = result
    else:
        with ProcessPoolExecutor(max_workers=dataset_workers) as executor:
            for name, result in tqdm(
                executor.map(_fit_and_bootstrap_one, tasks),
                total=n_datasets,
                desc=f"Datasets (n_jobs={dataset_workers})",
                unit="dataset",
            ):
                results[name] = result

    return results


if __name__ == "__main__":
    # Small runnable demo: fit a noisy sphere form factor (no structure factor).
    q = np.linspace(0.001, 0.5, 100)

    true_params = {
        "scale": 1.0,
        "background": 0.001,
        "sld": 4.0e-6,
        "sld_solvent": 1.0e-6,
        "radius": 50.0,
    }

    I = intensity(q, form_factor_model="sphere", **true_params)

    plt.figure()
    plt.plot(q, I)
    plt.xscale("log")
    plt.yscale("log")
    plt.xlabel("q")
    plt.ylabel("Intensity")
    plt.savefig("test_intensity_plot.png", dpi=300)
    plt.close()

    rng = np.random.default_rng(0)
    I_noisy = I + rng.normal(0, 0.02 * I.max(), size=I.shape)

    plt.figure()
    plt.scatter(q, I_noisy, label="Noisy data", s=10)
    plt.plot(q, I, "-", label="True intensity", color="red")
    plt.xscale("log")
    plt.yscale("log")
    plt.xlabel("q")
    plt.ylabel("Intensity")
    plt.legend()
    plt.savefig("test_noisy_intensity_plot.png", dpi=300)
    plt.close()

    initial_params = {**true_params, "radius": 40.0}
    fit_params = {
        "scale": False,
        "background": False,
        "sld": False,
        "sld_solvent": False,
        "radius": True,
    }

    popt, pcov, param_order = fit_data(
        q,
        I_noisy,
        form_factor_model="sphere",
        initial_params=initial_params,
        fit_params=fit_params,
    )

    print("Fitted parameters:", dict(zip(param_order, popt)))
