"""
Core Analysis Utilities for Small-Angle Scattering (SAS)

This is the main analysis module of the ECHEMES bootstrapping framework, providing 
comprehensive tools for fitting, uncertainty analysis, and visualization of small-angle 
scattering data using core-shell cylinder models with optional structure factor corrections.

Key Components:
==============

Scattering Models:
- Core-shell cylinder form factors with high-performance C implementations
- Hayter-Penfold MSA structure factors for charged particle interactions  
- Automatic model selection based on available parameters

Parameter Fitting:
- Robust non-linear least squares fitting using scipy.optimize
- Flexible parameter bounds and fitting constraints
- Support for both form-factor-only and full structure factor fits
- Multiple optimization algorithms (Levenberg-Marquardt, Trust Region, etc.)

Bootstrap Uncertainty Analysis:
- Residuals bootstrap resampling for uncertainty quantification
- Configurable number of bootstrap iterations
- Automatic confidence interval calculation
- Progress tracking with tqdm integration

Visualization Tools:
- Data plotting with customizable styling
- Fit overlay plots with residuals
- Batch plotting with automatic file management
- Publication-ready figure generation

Default Parameters:
- Pre-configured initial parameters for common SAS measurements
- Flexible parameter dictionaries for easy customization
- Built-in parameter validation and bounds checking

Functions Overview:
==================
- form_factor(), structure_factor(), intensity() - Core scattering calculations
- fit_data() - Main parameter fitting function
- residuals_bootstrap() - Uncertainty analysis via bootstrap resampling  
- compute_confidence_intervals() - Statistical analysis of bootstrap results
- plot_data(), plot_fit_data() - Visualization and plotting utilities

Usage:
======
This module is designed for both interactive analysis and automated batch processing.
All functions use keyword argument dictionaries for maximum flexibility and easy 
integration with different scattering models.

Example:
    from utils import fit_data, residuals_bootstrap, plot_fit_data
    
    # Fit experimental data
    fitted_params, covariance = fit_data(q_data, I_data)
    
    # Quantify uncertainties
    bootstrap_results = residuals_bootstrap(q_data, I_data, fitted_params)
    
    # Visualize results  
    plot_fit_data(q_data, I_data, fitted_params)
"""

import os
import sys
import importlib
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from tqdm import tqdm
from scipy.optimize import curve_fit

# ==================== MODEL CONFIGURATION ====================
# Define the models to use for form factor and structure factor
# These should match directory names in src/form_factor/ and src/structure_factor/
# NOTE: Onion and core_multi_shell form factor are not fully supported yet with all features.
FORM_FACTOR_MODEL = "barbell"
STRUCTURE_FACTOR_MODEL = "hayter_msa"

# NOTE: Adjust the vectorized functions and model relevant parameters below!

# ==================== DYNAMIC MODEL LOADING ====================
def _load_models():
    """
    Dynamically load form factor and structure factor models based on configuration.
    
    Returns
    -------
    tuple
        (form_factor_module, structure_factor_module) containing the loaded wrapper modules
    """
    # Load form factor model
    form_factor_path = f"form_factor.{FORM_FACTOR_MODEL}.wrapper"
    try:
        form_factor_module = importlib.import_module(form_factor_path)
    except ImportError as e:
        raise ImportError(
            f"Failed to import form factor model '{FORM_FACTOR_MODEL}' from '{form_factor_path}'. "
            f"Ensure the model exists in src/form_factor/{FORM_FACTOR_MODEL}/wrapper.py. "
            f"Error: {e}"
        )
    
    # Load structure factor model
    structure_factor_path = f"structure_factor.{STRUCTURE_FACTOR_MODEL}.wrapper"
    try:
        structure_factor_module = importlib.import_module(structure_factor_path)
    except ImportError as e:
        raise ImportError(
            f"Failed to import structure factor model '{STRUCTURE_FACTOR_MODEL}' from '{structure_factor_path}'. "
            f"Ensure the model exists in src/structure_factor/{STRUCTURE_FACTOR_MODEL}/wrapper.py. "
            f"Error: {e}"
        )
    
    return form_factor_module, structure_factor_module

# Load the models
_form_factor_module, _structure_factor_module = _load_models()

# Extract the compute functions from the loaded modules
compute_form_factor = _form_factor_module.compute_form_factor
compute_structure_factor = _structure_factor_module.compute_structure_factor

def form_factor(q, **kwargs):
    """
    Compute the form factor for the FORM_FACTOR_MODEL model.

    Parameters
    ----------
    q : float
        The scattering vector magnitude.
    **kwargs : dict
        Additional keyword arguments for model parameters.

    Returns
    -------
    tuple of float
        The integrated computed form factor (F) and form factor squared (F²).
    """
    return compute_form_factor(q, **kwargs)

def form_factor_2(q, scale, background, **kwargs):
    """
    Compute the form factor squared for the FORM_FACTOR_MODEL model.

    Parameters
    ----------
    q : float
        The scattering vector magnitude.
    scale : float
        Scale factor.
    background : float
        Background intensity.
    **kwargs : dict
        Additional keyword arguments for model parameters.

    Returns
    -------
    float
        The intensity I(q) = scale * F² + background.
    """
    return scale * compute_form_factor(q, **kwargs) + background

def structure_factor(q, **kwargs):
    """
    Compute the structure factor using the Hayter-Penfold MSA model.

    Parameters
    ----------
    q : float
        The scattering vector magnitude.
    **kwargs : dict
        Additional keyword arguments for model parameters.

    Returns
    -------
    float
        The structure factor S(q).
    """
    return compute_structure_factor(q, **kwargs)

def intensity(q, scale, background, **kwargs):
    """
    Compute the total scattering intensity including both form factor and structure factor.

    Parameters
    ----------
    q : float
        The scattering vector magnitude.
    scale : float
        Scale factor.
    background : float
        Background intensity.
    **kwargs : dict
        Additional keyword arguments for model parameters.

    Returns
    -------
    float
        Total scattering intensity I(q) = scale * (F² * S(q)) + background.
    """
    F2 = compute_form_factor(q, **kwargs)
    S_q = compute_structure_factor(q, **kwargs)

    return scale * (F2 * S_q) + background


# ==================== FITTING METHOD SPECIFICATIONS ====================

# NOTE: Adjust the vectorized functions and dicts below:
# Example: Onion form factor with Hayter-Penfold MSA structure factor

# Vectorized version of the form factor function for fitting (for scipy.optimize.curve_fit) (used when the structure factor is negligible)
form_factor_for_fitting = np.vectorize(form_factor_2, excluded=['scale', 'background', 'sld', 'solvent_sld', 'radius_bell', 'radius', 'length'])

# Vectorized version of the intensity function for fitting (for scipy.optimize.curve_fit)
intensity_for_fitting = np.vectorize(intensity, excluded=['scale', 'background', 'sld', 'solvent_sld', 'radius_bell', 'radius', 'length',
                                                         'radius_effective', 'volfraction', 'charge', 'temperature', 'saltconc', 'dielectconst'])

initial_params = {
    "scale": 1,
    "background": 0.001,
    "sld": 4.0e-6,
    "solvent_sld": 1.0e-6,
    "radius_bell": 20.0,
    "radius": 10.0,
    "length": 50.0,
    "radius_effective": 24.8,
    "volfraction": 0.16363,
    "charge": 28.288,
    "temperature": 300,
    "saltconc": 0.093723,
    "dielectconst": 78.3
}

fit_params = {
    "scale": True,
    "background": True,
    "sld": True, # Do
    "solvent_sld": False,
    "radius_bell": True, # Do
    "radius": True, # Do
    "length": True, # Do
    "radius_effective": True, # Do
    "volfraction": True, # Do
    "charge": True, # Do
    "temperature": False,
    "saltconc": True, # Do
    "dielectconst": False
}

def fit_data(x_data, y_data, initial_params=initial_params, fit_params=fit_params, bounds=(-np.inf, np.inf), method='lm', structure_factor=True):
    """
    Fit experimental data to the scattering model using non-linear least squares.

    Parameters
    ----------
    x_data : array_like
        Independent variable data (scattering vector q).
    y_data : array_like
        Dependent variable data (intensity I).
    initial_params : dict, optional
        Initial parameter values for fitting. Possible keys: 'scale', 'background',
        'core_sld', 'shell_sld', 'solvent_sld', 'radius', 'thickness', 'length',
        'radius_effective', 'vol_frac', 'zz', 'temp', 'csalt', 'dialec'.
        Default is the module-level initial_params.
    fit_params : dict, optional
        Dictionary indicating which parameters to fit (True) and which to keep fixed (False).
        Should match keys in initial_params. Default is the module-level fit_params.
    bounds : tuple of array_like or dict, optional
        Lower and upper bounds for parameters to be fitted. Can be a 2-tuple of arrays
        or a dict mapping parameter names to (lower, upper) tuples.
        Default is (-np.inf, np.inf).
    method : str, optional
        Fitting method for scipy.optimize.curve_fit. Options include 'lm'
        (Levenberg-Marquardt), 'trf' (Trust Region Reflective), 'dogbox'.
        Default is 'lm'.
    structure_factor : bool, optional
        Whether to include the structure factor in the intensity calculation.
        If False, only form factor is used. Default is True.

    Returns
    -------
    popt : ndarray
        Optimal values for the fitted parameters.
    pcov : ndarray
        Covariance matrix of popt. The diagonals provide variance of parameter estimates.
    param_order : list of str
        Names of the parameters that were fitted, in the order they appear in popt.
    """

    if not any(isinstance(x, (np.ndarray, list, tuple)) for x in t):
        param_order = [name for name in fit_params.keys() if fit_params[name]] # Get the order of parameters to fit (and their names)
        mask = [0] * len(param_order)
        if type(bounds) is dict:
            lower_bounds = [bounds[name][0] for name in param_order]
            upper_bounds = [bounds[name][1] for name in param_order]
            bounds = (lower_bounds, upper_bounds)

        def f(q, *fitting):
            if structure_factor:
                return intensity_for_fitting(q, 
                                **{name: fitting[param_order.index(name)] for name in param_order},
                                **{name: initial_params[name] for name in initial_params if name not in param_order})
            else:
                return form_factor_for_fitting(q, 
                                **{name: fitting[param_order.index(name)] for name in param_order},
                                **{name: initial_params[name] for name in initial_params if name not in param_order})
    else:
        param_order = []
        new_initial_params = {}

        mask = [] # For the function f below to know where the lists were flattened

        with_bounds = False

        if type(bounds) is dict:
            with_bounds = True
            lower_bounds = []
            upper_bounds = []

        for v, x in fit_params.items():
            if isinstance(x, (list, tuple, np.ndarray)):
                mask.append(-1)
                for i in range(len(x)):
                    if x[i]:
                        param_order.append(f"{v}_{i}")
                        new_initial_params[f"{v}_{i}"] = initial_params[v][i]
                    if with_bounds:
                        lower_bounds.append(bounds[v][i][0])
                        upper_bounds.append(bounds[v][i][1])

                    mask.append(1) if x[i] else None

            else:
                param_order.append(v) if x else None
                new_initial_params[v] = initial_params[v]
                mask.append(0) if x else None

                if with_bounds:
                    lower_bounds.append(bounds[v][0])
                    upper_bounds.append(bounds[v][1])
        initial_params = new_initial_params

    def f(q, *fitting):
        if structure_factor:
            reconstructed = {}
            names_to_exclude = []


            real_counter = 0
            beginning_list = False
            for i in mask:
                if beginning_list and i == -1: # If the previous list was empty and there is another one following
                    continue
                elif beginning_list and i == 0: # If the previous list was empty
                    beginning_list = False

                if i == 0: # No list
                    reconstructed[param_order[real_counter]] = fitting[real_counter]
                    names_to_exclude.append(param_order[real_counter])
                    real_counter += 1
                elif i == -1: # Beginning of a list
                    beginning_list = True
                    continue
                elif i == 1: # Inside a list
                    name = param_order[real_counter][:-2] # Remove the _i suffix
                    if name not in reconstructed:
                        reconstructed[name] = []
                    reconstructed[name].append(fitting[real_counter])
                    names_to_exclude.append(param_order[real_counter])
                    real_counter += 1

            reconstructed.update({name: initial_params[name] for name in initial_params if name not in names_to_exclude})
            return intensity_for_fitting(q, **reconstructed)
        else:
            return form_factor_for_fitting(q, 
                            **{name: fitting[param_order.index(name)] for name in param_order},
                            **{name: initial_params[name] for name in initial_params if name not in param_order})

    try:
        popt, pcov = curve_fit(
            f, 
            x_data, 
            y_data, 
            p0=[initial_params[name] for name in param_order],
            bounds=bounds,
            method=method,
            maxfev=2000
        )
    except Exception as e:
        print(f"Error during curve fitting: {e}\nMoving on to next one.")
        return np.empty((len(param_order),)), np.empty((len(param_order), len(param_order))), param_order
    # except RuntimeError as e:
    #     print(f"Error during curve fitting: {e}")
    #     popt = e.args[1]
    #     pcov = None
    # except Exception as e:
    #     print(f"Unexpected error during curve fitting: {e}")
    #     popt = [initial_params[name] for name in param_order]
    #     pcov = None

    return popt, pcov, param_order

def plot_data(xdata, ydata, title="Data Plot", xlabel="q", ylabel="Intensity"):
    """
    Plot experimental data points.

    Parameters
    ----------
    xdata : array_like
        Independent variable data (typically scattering vector q).
    ydata : array_like
        Dependent variable data (typically intensity I).
    title : str, optional
        Title of the plot. Default is "Data Plot".
    xlabel : str, optional
        Label for the x-axis. Default is "q".
    ylabel : str, optional
        Label for the y-axis. Default is "Intensity".

    Returns
    -------
    None
        Saves plot as PNG file with filename derived from title.
    """

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.scatter(xdata, ydata, label='Data', color='blue', s=10)

    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.legend()
    ax.grid(True)
    
    plt.savefig(f"{title.replace(' ', '_').lower()}.png", dpi=300)
    plt.close(fig)

def plot_fit_data(xdata, ydata, params, title="Fit Data", xlabel="q", ylabel="Intensity", folder=None, structure_factor=True):
    """
    Plot experimental data along with the fitted model curve.

    Parameters
    ----------
    xdata : array_like
        Independent variable data (typically scattering vector q).
    ydata : array_like
        Dependent variable data (typically intensity I).
    params : dict
        Dictionary of fitted parameters for the intensity function.
        Should contain all necessary parameters for the chosen model.
    title : str, optional
        Title of the plot. Default is "Fit Data".
    xlabel : str, optional
        Label for the x-axis. Default is "q".
    ylabel : str, optional
        Label for the y-axis. Default is "Intensity".
    folder : str, optional
        Folder path to save the plot. If None, saves to current working directory.
        Default is None.
    structure_factor : bool, optional
        Whether to include the structure factor in the intensity calculation.
        If False, only form factor is used. Default is True.

    Returns
    -------
    None
        Saves plot as PNG file in the specified folder.
    """

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.scatter(xdata, ydata, label='Data', color='blue', s=10)

    if structure_factor:
        fitted_y = intensity_for_fitting(xdata, **params)
    else:
        fitted_y = form_factor_for_fitting(xdata, **params)

    ax.loglog(xdata, fitted_y, label='Fitted Curve', color='red')

    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.legend()
    ax.grid(True)
    
    if not folder:
        folder = os.getcwd()
    plt.savefig(os.path.join(folder, f"{title.replace(' ', '_').lower()}.png"), dpi=300)
    plt.close(fig)

def residuals_bootstrap(x_data, y_data, all_params=initial_params, fit_params=fit_params, n_iterations=1000, bounds=(-np.inf, np.inf), store=None, method="lm", structure_factor=True):
    """
    Perform residuals bootstrap resampling to quantify parameter uncertainties.

    This function implements the residuals bootstrap method for uncertainty quantification.
    It resamples residuals from the initial fit, creates synthetic datasets, refits each
    synthetic dataset, and stores the results for confidence interval calculation.

    Parameters
    ----------
    x_data : array_like
        Independent variable data (scattering vector q).
    y_data : array_like
        Dependent variable data (intensity I).
    all_params : dict, optional
        Parameter values including fitted parameters from the original fit.
        Should have the same keys as fit_params and work with the intensity function.
        Default is the module-level initial_params.
    fit_params : dict, optional
        Dictionary indicating which parameters to fit (True) and which to keep fixed (False).
        Default is the module-level fit_params.
    n_iterations : int, optional
        Number of bootstrap iterations to perform. Default is 1000.
    bounds : tuple of array_like or dict, optional
        Lower and upper bounds for parameters to be fitted.
        Default is (-np.inf, np.inf).
    store : pd.HDFStore, optional
        HDF5 store object to save bootstrap samples. If provided, stores residuals,
        synthetic_y data, and fitted_params for each iteration. Default is None.
    method : str, optional
        Fitting method for scipy.optimize.curve_fit. Options include 'lm'
        (Levenberg-Marquardt), 'trf' (Trust Region Reflective).
        Default is "lm".
    structure_factor : bool, optional
        Whether to include the structure factor in the intensity calculation.
        If False, only form factor is used. Default is True.

    Returns
    -------
    list of dict
        List of parameter dictionaries, one for each bootstrap iteration.
        Each dictionary contains all parameters (fitted and fixed) for that iteration.

    Notes
    -----
    Progress is displayed using tqdm with time estimates. Every 25 iterations,
    elapsed and estimated remaining time is printed.
    """

    if type(y_data) is not np.ndarray:
        y_data = np.array(y_data)

    fit_arr = []

    # Compute the fitted intensity using the current parameters
    if structure_factor:
        fitted_y = intensity_for_fitting(x_data, **all_params)
    else:
        fitted_y = form_factor_for_fitting(x_data, **all_params)
    residuals = y_data - fitted_y

    if store is not None:
        store.put('residuals', pd.Series(residuals))

    import time
    start_time = time.time()
    
    for i in tqdm(range(n_iterations), desc="Bootstrapping residuals", unit="iteration"):
        # Estimate remaining time after first few iterations
        if i > 0:
            elapsed_time = time.time() - start_time
            avg_time_per_iteration = elapsed_time / i
            remaining_iterations = n_iterations - i
            estimated_total_time = avg_time_per_iteration * n_iterations
            estimated_remaining_time = avg_time_per_iteration * remaining_iterations
            
            if i % 25 == 0:
                tqdm.write(f"Iteration {i}/{n_iterations} - Elapsed: {elapsed_time:.1f}s - "
                      f"Est. total: {estimated_total_time:.1f}s - Est. remaining: {estimated_remaining_time:.1f}s")
        
        # Here: All residuals are resamples. In the future, it could be interesting to examine what would change if only a fraction were resampled.
        resampled = np.random.choice(residuals, size=len(residuals), replace=True)  # Randomly sample residuals with replacement for bootstrapping
        synthetic_y = y_data + resampled

        if store is not None:
            store.put(f'synthetic_y/s{str(i)}', pd.Series(synthetic_y))

        new_fitted_params, _, param_order = fit_data(x_data, synthetic_y, all_params, fit_params, bounds=bounds, method=method, structure_factor=structure_factor)
        
        new_fitted_params = dict(zip(param_order, new_fitted_params))

        if store is not None:
            store.put(f'fitted_params/s{str(i)}', pd.Series(new_fitted_params))

        # Plot the fit for the first few iterations to visualize the fitting process:
        #plot_fit_data(x_data, synthetic_y, {key: new_fitted_params[key] if fit_params[key] else all_params[key] for key in all_params.keys()}, title=f"Bootstrap Fit Iteration {i+1}", xlabel="q", ylabel="Intensity", folder=f"bootstrap_fit_plotting") # TODO: Could be updated to include the structure_factor (bool) argument

        fit_arr.append({key: new_fitted_params[key] if fit_params[key] else all_params[key] for key in all_params.keys()})

    return fit_arr

def compute_confidence_intervals(fitted_params, confidence_level=0.05):
    """
    Compute confidence intervals from bootstrap parameter distributions.

    Calculates percentile-based confidence intervals from bootstrap samples using the
    formula: [p*(B·α/2), p*(B·(1-α/2))], where B is the number of bootstrap samples
    and α is the confidence level.

    Parameters
    ----------
    fitted_params : list of dict
        List of parameter dictionaries from bootstrap samples.
        Each dictionary should have the same keys representing parameter names.
    confidence_level : float, optional
        Significance level for the confidence intervals. For example, 0.05 gives
        95% confidence intervals (2.5th to 97.5th percentiles). Default is 0.05.

    Returns
    -------
    dict
        Dictionary mapping parameter names to (lower_bound, upper_bound) tuples.
        Bounds are computed using the 'nearest' percentile method.

    Notes
    -----
    The confidence intervals are calculated using numpy.percentile with method='nearest',
    which selects the closest data point rather than interpolating.
    """
    
    dict_of_lists = {key: np.array([d[key] for d in fitted_params]) for key in fitted_params[0].keys()}

    param_order = list(dict_of_lists.keys())
    arr_fitted_params = np.array([dict_of_lists[key] for key in param_order]).T

    lower_bound = np.percentile(arr_fitted_params, (confidence_level / 2) * 100, method="nearest", axis=0)
    upper_bound = np.percentile(arr_fitted_params, (1 - confidence_level / 2) * 100, method="nearest", axis=0)

    return {param_order[i]: (lower_bound[i], upper_bound[i]) for i in range(len(param_order))}


if __name__ == "__main__":
    import numpy as np
    x = np.linspace(0.001, 0.5, 100)
    y = intensity_for_fitting(x, **initial_params)
    print("y:", y)
    import matplotlib.pyplot as plt
    plt.plot(x, y)
    plt.yscale('log')
    plt.savefig("test_intensity_plot.png", dpi=300)

    t = list(fit_params.values())

    print(any(isinstance(x, (np.ndarray, list, tuple)) for x in t))

    q = np.linspace(0.01, 0.5, 100)
    I = intensity_for_fitting(q, **initial_params)
    noise_level = 0.0001 * np.max(I)
    I_noisy = I + np.random.normal(0, noise_level, size=I.shape)
    plt.scatter(q, I_noisy, label='Noisy Data')
    plt.plot(q, I, '-', label='True Intensity')
    plt.yscale('log')
    plt.xlabel('q')
    plt.ylabel('Intensity')
    plt.legend()
    plt.savefig("test_noisy_intensity_plot.png", dpi=300)

    a, b, c = fit_data(q, I_noisy, initial_params, fit_params)

    print(c)
    print(a)
