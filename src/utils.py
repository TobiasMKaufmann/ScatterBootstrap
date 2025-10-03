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

from core_shell_cylinder.wrapper import compute_form_factor
from core_shell_cylinder.hayter_msa_wrapper import compute_structure_factor
from scipy.optimize import curve_fit
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from tqdm import tqdm
import os

def form_factor(q, core_sld, shell_sld, solvent_sld, radius, thickness, length):
    """
    Compute the form factor for the core-shell cylinder model.

    Parameters
    ----------
    q : float
        The scattering vector magnitude.
    core_sld : float
        The scattering length density of the core.
    shell_sld : float
        The scattering length density of the shell.
    solvent_sld : float
        The scattering length density of the solvent.
    radius : float
        The radius of the core.
    thickness : float
        The thickness of the shell.
    length : float
        The length of the cylinder.

    Returns
    -------
    tuple of float
        The integrated computed form factor (F) and form factor squared (F²).
    """
    return compute_form_factor(q, core_sld, shell_sld, solvent_sld, radius, thickness, length)

def form_factor_2(q, core_sld, shell_sld, solvent_sld, radius, thickness, length, scale, background):
    """
    Compute the form factor squared for the core-shell cylinder model.

    Parameters
    ----------
    q : float
        The scattering vector magnitude.
    core_sld : float
        The scattering length density of the core.
    shell_sld : float
        The scattering length density of the shell.
    solvent_sld : float
        The scattering length density of the solvent.
    radius : float
        The radius of the core.
    thickness : float
        The thickness of the shell.
    length : float
        The length of the cylinder.
    scale : float
        Scale factor.
    background : float
        Background intensity.

    Returns
    -------
    float
        The intensity I(q) = scale * F² + background.
    """
    return scale * compute_form_factor(q, core_sld, shell_sld, solvent_sld, radius, thickness, length)[1] + background

# Vectorized version of the form factor function for fitting (for scipy.optimize.curve_fit) (used when the structure factor is negligible)
form_factor_for_fitting = np.vectorize(form_factor_2, excluded=['scale', 'background', 'core_sld', 'shell_sld', 'solvent_sld', 'radius', 'thickness', 'length'])

def structure_factor(q, radius_effective, volume_fraction, charge, temperature, salt_concentration, dielectric_constant):
    """
    Compute the structure factor using the Hayter-Penfold MSA model.

    Parameters
    ----------
    q : float
        The scattering vector magnitude.
    radius_effective : float
        Effective radius of the particles.
    volume_fraction : float
        Volume fraction of the particles.
    charge : float
        Particle charge number.
    temperature : float
        Temperature in Kelvin.
    salt_concentration : float
        Salt concentration in Molarity.
    dielectric_constant : float
        Dielectric constant of the solvent.

    Returns
    -------
    float
        Structure factor S(q).
    """
    return compute_structure_factor(q, radius_effective, volume_fraction, charge, temperature, salt_concentration, dielectric_constant)

def intensity(q, scale, background, core_sld, shell_sld, solvent_sld, radius, thickness, length, radius_effective, vol_frac, zz, temp, csalt, dialec):
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
    core_sld : float
        The scattering length density of the core.
    shell_sld : float
        The scattering length density of the shell.
    solvent_sld : float
        The scattering length density of the solvent.
    radius : float
        The radius of the core.
    thickness : float
        The thickness of the shell.
    length : float
        The length of the cylinder.
    radius_effective : float
        Effective radius of the particles.
    vol_frac : float
        Volume fraction of the particles.
    zz : float
        Particle charge number.
    temp : float
        Temperature in Kelvin.
    csalt : float
        Salt concentration in Molarity.
    dialec : float
        Dielectric constant of the solvent.

    Returns
    -------
    float
        Total scattering intensity I(q) = scale * (F² * S(q)) + background.
    """
    _, F2 = compute_form_factor(q, core_sld, shell_sld, solvent_sld, radius, thickness, length)
    S_q = compute_structure_factor(q, radius_effective, vol_frac, zz, temp, csalt, dialec)

    return scale * (F2 * S_q) + background


# Vectorized version of the intensity function for fitting (for scipy.optimize.curve_fit)
intensity_for_fitting = np.vectorize(intensity, excluded=['scale', 'background', 'core_sld', 'shell_sld', 'solvent_sld', 'radius', 'thickness', 'length',
                                                         'radius_effective', 'vol_frac', 'zz', 'temp', 'csalt', 'dialec'])

initial_params = {
    "scale": 1,
    "background": 0.001,
    "core_sld": 7.7,
    "shell_sld": 10.989,
    "solvent_sld": 9.4,
    "radius": 13.84,
    "thickness": 6.60,
    "length": 35.21,
    "radius_effective": 24.8,
    "vol_frac": 0.16363,
    "zz": 28.288,
    "temp": 300,
    "csalt": 0.093723,
    "dialec": 78.3
}

fit_params = {
    "scale": True,
    "background": True,
    "core_sld": False,
    "shell_sld": False,
    "solvent_sld": False,
    "radius": True, # Do
    "thickness": True, # Do
    "length": True, # Do
    "radius_effective": True, # Do
    "vol_frac": True, # Do
    "zz": True, # Do
    "temp": False,
    "csalt": True, # Do
    "dialec": False
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

    param_order = [name for name in fit_params.keys() if fit_params[name]] # Get the order of parameters to fit (and their names)
    
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

    try:
        popt, pcov = curve_fit(
            f, 
            x_data, 
            y_data, 
            p0=[initial_params[name] for name in param_order],
            bounds=bounds,
            method=method,
            maxfev=1000
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

        store.put(f'synthetic_y/s{str(i)}', pd.Series(synthetic_y))

        new_fitted_params, _, param_order = fit_data(x_data, synthetic_y, all_params, fit_params, bounds=bounds, method=method, structure_factor=structure_factor)
        
        new_fitted_params = dict(zip(param_order, new_fitted_params))

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
