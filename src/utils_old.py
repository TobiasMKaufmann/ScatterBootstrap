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

    Parameters:
    q (float): The scattering vector magnitude.
    core_sld (float): The scattering length density of the core.
    shell_sld (float): The scattering length density of the shell.
    solvent_sld (float): The scattering length density of the solvent.
    radius (float): The radius of the core.
    thickness (float): The thickness of the shell.
    length (float): The length of the cylinder.

    Returns:
    float: The integrated computed form factor.
    float: The integrated computed form factor squared.
    """
    return compute_form_factor(q, core_sld, shell_sld, solvent_sld, radius, thickness, length)

def form_factor_2(q, core_sld, shell_sld, solvent_sld, radius, thickness, length, scale, background):
    """
    Compute the form factor squared for the core-shell cylinder model.

    Parameters:
    q (float): The scattering vector magnitude.
    core_sld (float): The scattering length density of the core.
    shell_sld (float): The scattering length density of the shell.
    solvent_sld (float): The scattering length density of the solvent.
    radius (float): The radius of the core.
    thickness (float): The thickness of the shell.
    length (float): The length of the cylinder.
    scale (float): Scale factor for the intensity.
    background (float): Background intensity.

    Returns:
    float: The integrated computed form factor squared.
    """
    _, F2 = compute_form_factor(q, core_sld, shell_sld, solvent_sld, radius, thickness, length)
    return scale * F2 + background

# Vectorized version of the form factor function for fitting (for scipy.optimize.curve_fit) (used when the structure factor is negligible)
form_factor_for_fitting = np.vectorize(form_factor_2, excluded=['scale', 'background', 'core_sld', 'shell_sld', 'solvent_sld', 'radius', 'thickness', 'length'])

def structure_factor(q, radius_effective, volume_fraction, charge, temperature, salt_concentration, dielectric_constant):
    """
    Compute the Hayter-Penfold MSA structure factor.
    
    Parameters:
    q (float): Scattering vector (1/Å)
    radius_effective (float): Effective radius (Å)
    volume_fraction (float): Volume fraction (dimensionless)
    charge (float): Particle charge (elementary charges)
    temperature (float): Temperature (K)
    salt_concentration (float): Salt concentration (M)
    dielectric_constant (float): Dielectric constant (dimensionless)

    Returns:
    float: Structure factor S(q)
    """
    return compute_structure_factor(q, radius_effective, volume_fraction, charge, temperature, salt_concentration, dielectric_constant)

def intensity(q, scale, background, core_sld, shell_sld, solvent_sld, radius, thickness, length, radius_effective, vol_frac, zz, temp, csalt, dialec):
    """
    Compute the total scattering intensity I(q) = F²(q) × S(q).

    Parameters:
    q (float): Scattering vector.
    scale (float): Scale factor for the intensity.
    background (float): Background intensity.
    core_sld (float): Core scattering length density.
    shell_sld (float): Shell scattering length density.
    solvent_sld (float): Solvent scattering length density.
    radius (float): Core radius.
    thickness (float): Shell thickness.
    length (float): Length of the cylinder.
    radius_effective (float): Effective radius.
    vol_frac (float): Volume fraction.
    zz (float): Particle charge.
    temp (float): Temperature in Kelvin.
    csalt (float): Salt concentration in Molarity.
    dialec (float): Dielectric constant.

    Returns:
    float: Total scattering intensity I(q).
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
    x_data (list): Independent variable data.
    y_data (list): Dependent variable data.
    initial_params (dict): Initial parameter values for fitting.
                            Possible keys: 'scale', 'background', 'core_sld', 'shell_sld', 'solvent_sld', 'radius', 'thickness',
                                  'length', 'radius_effective', 'vol_frac', 'zz', 'temp', 'csalt', 'dialec'.
    fit_params (dict): Parameters to fit, with True for fitting and False for fixed values.
                        Should match keys in initial_params.
    bounds (2-tuple of array-like, optional): Lower and upper bounds for parameters to be fitted.
    method (str): Fitting method, e.g., 'lm' (uses scipy.optimize.curve_fit). 
    structure_factor (bool): Whether to include the structure factor in the intensity calculation.
                                If this is False, the dicts provided above should be updated accordingly.

    Returns:
    popt (array): Optimal values for the parameters.
    pcov (2D array): Covariance of popt.
    param_order (list): Names of the parameters that were fitted.
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
    Plot the data points.

    Parameters:
    xdata (array): Independent variable data.
    ydata (array): Dependent variable data.
    title (str): Title of the plot.
    xlabel (str): Label for the x-axis.
    ylabel (str): Label for the y-axis.
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
    Plot the fit data along with the fitted curve.

    Parameters:
    xdata (array): Independent variable data.
    ydata (array): Dependent variable data.
    params (dict): Fitted parameters for the intensity function.
    title (str): Title of the plot.
    xlabel (str): Label for the x-axis.
    ylabel (str): Label for the y-axis.
    folder (str): Folder to save the plot.
    structure_factor (bool): Whether to include the structure factor in the intensity calculation.
                                If this is False, params should be updated accordingly.
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


def bootstrapping(x_data, y_data, n_iterations=1000, block_size=5):
    """
    Perform block bootstrapping to generate varied datasets from time-series data while preserving temporal structure.
    How it works:
    - Randomly selects blocks of data points to create bootstrap samples.
    - Each block is a contiguous segment of the time-series data.
    - It is possible that some data points may be repeated in the bootstrap sample and some may not be included at all.

    Parameters:
    x_data (array): Independent variable data (time-series x values).
    y_data (array): Dependent variable data (time-series y values).
    n_iterations (int): Number of bootstrap iterations.
    initial_params (dict): Initial parameter values for fitting.
    fit_params (dict): Parameters to fit.
    block_size (int): Size of blocks to sample (preserves local temporal structure).

    Returns:
    array: Array of bootstrap samples (x_bootstrap, y_bootstrap) for each iteration.
    """
    bootstrap_samples = []
    n_data = len(x_data)
    
    for iteration in range(n_iterations):
        # Create bootstrap sample using block sampling
        x_bootstrap = []
        y_bootstrap = []
        
        # Sample blocks until we have enough data points
        while len(x_bootstrap) < n_data:
            # Randomly select a starting position for the block
            start_idx = np.random.randint(0, max(1, n_data - block_size + 1))
            end_idx = min(start_idx + block_size, n_data)
            
            # Add the block to bootstrap sample
            x_bootstrap.extend(x_data[start_idx:end_idx])
            y_bootstrap.extend(y_data[start_idx:end_idx])
        
        # Trim to original length
        x_bootstrap = np.array(x_bootstrap[:n_data])
        y_bootstrap = np.array(y_bootstrap[:n_data])
        
        # Store bootstrap sample
        bootstrap_samples.append((x_bootstrap, y_bootstrap))

        # Plot the first few iterations to visualize the bootstrap process
        if iteration < 1:  # Plot first 5 iterations
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))

            # Top plot: Original data
            ax1.plot(x_data, y_data, 'o-', color='blue', markersize=4, 
                    linewidth=2, label='Original Data', alpha=0.8)
            ax1.set_title(f"Original Time Series Data")
            ax1.set_ylabel("Intensity I(q)")
            ax1.legend()
            ax1.grid(True, alpha=0.3)
            
            # Bottom plot: Bootstrap sample
            ax2.scatter(x_bootstrap, y_bootstrap, color='red', s=16, label=f'Bootstrap Sample {iteration + 1}', alpha=0.8)
            ax2.set_title(f"Bootstrap Sample {iteration + 1} (Block Size = {block_size})")
            ax2.set_xlabel("Scattering Vector q (1/Å)")
            ax2.set_ylabel("Intensity I(q)")
            ax2.legend()
            ax2.grid(True, alpha=0.3)

            plt.tight_layout()
            plt.savefig(f"bootstrap_iteration_{iteration + 1}.png", dpi=300)
            plt.close(fig)
        
        # Print progress every 100 iterations
        if (iteration + 1) % 100 == 0:
            print(f"Completed {iteration + 1}/{n_iterations} bootstrap iterations")

    return np.array(bootstrap_samples)

def fit_bootstrap_samples(bootstrap_samples, initial_params=initial_params, fit_params=fit_params):
    """
    Fit the bootstrap samples to extract fitted parameters.

    Parameters:
    bootstrap_samples (array): Array of bootstrap samples (x_bootstrap, y_bootstrap).
    initial_params (dict): Initial parameter values for fitting.
    fit_params (dict): Parameters to fit.

    Returns:
    list: List of fitted parameters for each bootstrap sample.
    """
    fitted_params = []

    for x_bootstrap, y_bootstrap in tqdm(bootstrap_samples, desc="Fitting bootstrap samples", unit="sample"):
        popt, pcov, param_order = fit_data(x_bootstrap, y_bootstrap, initial_params, fit_params)
        fitted_params.append(dict(zip(param_order, popt)))

    return fitted_params

# I suggest this method:
def residuals_bootstrap(x_data, y_data, all_params=initial_params, fit_params=fit_params, n_iterations=1000, bounds=(-np.inf, np.inf), store=None, method="lm", structure_factor=True):
    """
    Compute residuals for each bootstrap sample.

    Parameters:
    x_data (array): Independent variable data.
    y_data (array): Dependent variable data.
    all_params (dict): Initial parameter values (including the fitted ones from the original fit) for fitting.
                        This should have the same keys as fit_params and work with the intensity function.
    fit_params (dict): Parameters to fit.
    n_iterations (int): Number of bootstrap iterations.
    bounds (2-tuple of array-like, optional): Lower and upper bounds for parameters to be fitted.
    store (pd.HDFStore): HDF5 store to save the bootstrap samples.
    method (str): Fitting method, e.g., 'lm' (uses scipy.optimize.curve_fit).
    structure_factor (bool): Whether to include the structure factor in the intensity calculation.

    Returns:
    list: List of residuals for each bootstrap sample.
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
        
        resampled = np.random.choice(residuals, size=len(residuals), replace=True)  # Randomly sample residuals with replacement for bootstrapping
        synthetic_y = y_data + resampled

        store.put(f'synthetic_y/s{str(i)}', pd.Series(synthetic_y))

        if structure_factor:
            new_fitted_params, _, param_order = fit_data(x_data, synthetic_y, all_params, fit_params, bounds=bounds, method=method, structure_factor=structure_factor)
        else:
            new_fitted_params, _, param_order = fit_data(x_data, synthetic_y, all_params, fit_params, bounds=bounds, method=method, structure_factor=structure_factor)

        new_fitted_params = dict(zip(param_order, new_fitted_params))

        store.put(f'fitted_params/s{str(i)}', pd.Series(new_fitted_params))

        # Optional: Plot the fit for the first few iterations to visualize the fitting process
        #plot_fit_data(x_data, synthetic_y, {key: new_fitted_params[key] if fit_params[key] else all_params[key] for key in all_params.keys()}, title=f"Bootstrap Fit Iteration {i+1}", xlabel="q", ylabel="Intensity", folder=f"bootstrap_fit_plotting")

        fit_arr.append({key: new_fitted_params[key] if fit_params[key] else all_params[key] for key in all_params.keys()})

    return fit_arr

def compute_confidence_intervals(fitted_params, confidence_level=0.05):
    """
    Compute confidence intervals for the fitted parameters from bootstrap samples.
    The interval will be given as follows: [p*^(lower(B * \alpha/2)), p*^(upper(B * (1 - \alpha/2)))].
    B stands for the number of bootstrap samples.
    Parameters:
    fitted_params (list): List of dictionaries of fitted parameters from bootstrap samples. It is expected that each dictionary has the same keys.
    confidence_level (float): Confidence level for the intervals (default is 0.05 for 95% confidence).

    Returns:
    dict: Lower and upper bounds of the confidence intervals for each parameter as tuples.
    """
    
    dict_of_lists = {key: np.array([d[key] for d in fitted_params]) for key in fitted_params[0].keys()}

    param_order = list(dict_of_lists.keys())
    arr_fitted_params = np.array([dict_of_lists[key] for key in param_order]).T

    lower_bound = np.percentile(arr_fitted_params, (confidence_level / 2) * 100, method="nearest", axis=0)
    upper_bound = np.percentile(arr_fitted_params, (1 - confidence_level / 2) * 100, method="nearest", axis=0)

    return {param_order[i]: (lower_bound[i], upper_bound[i]) for i in range(len(param_order))}

# Deprecated
def bootstrapping_fit_test(x_data, y_data, n_iterations=1000, initial_params=initial_params, fit_params=fit_params, fixed_fraction=0.8):
    """
    Perform bootstrapping to estimate the uncertainty of the fitted parameters.

    Parameters:
    x_data (array): Independent variable data.
    y_data (array): Dependent variable data.
    n_iterations (int): Number of bootstrap iterations.
    initial_params (dict): Initial parameter values for fitting.
    fit_params (dict): Parameters to fit.
    fixed_fraction (float): Fraction of points to keep constant.

    Returns:
    list: List of fitted parameters from each bootstrap iteration.
    """
    bootstrap_results = []
    n_fixed = int(len(x_data) * fixed_fraction)

    for _ in range(n_iterations):
        # Select indices to keep fixed (same x, same y, same position)
        fixed_indices = np.random.choice(len(x_data), size=n_fixed, replace=False)
        
        # Create bootstrap sample: x stays the same, y gets modified for non-fixed indices
        x_bootstrap = x_data.copy()  # x values stay the same for all points
        y_bootstrap = y_data.copy()  # start with original y values
        
        # For non-fixed indices, replace y values with random samples from y_data
        non_fixed_indices = np.array([i for i in range(len(x_data)) if i not in fixed_indices])
        sampled_y_values = np.random.choice(y_data, size=len(non_fixed_indices), replace=True)
        y_bootstrap[non_fixed_indices] = sampled_y_values

        #popt, _, _ = fit_data(x_bootstrap, y_bootstrap, initial_params, fit_params)
        #bootstrap_results.append(popt)
        bootstrap_results.append((x_bootstrap, y_bootstrap))



        # Plot the result of one iteration
        if _ == 0:  # Plot only the first iteration
            fig, ax = plt.subplots(figsize=(10, 6))

            # Plot fixed points (unchanged x and y) in blue
            ax.scatter(x_bootstrap[fixed_indices], y_bootstrap[fixed_indices], label='Fixed Points', color='blue', s=10)
            
            # Plot resampled points (same x, new y values) in red
            ax.scatter(x_bootstrap[non_fixed_indices], y_bootstrap[non_fixed_indices], label='Resampled Y Values', color='red', s=10)

            ax.set_title("Bootstrapping Iteration 1")
            ax.set_xlabel("Scattering Vector q (1/Å)")
            ax.set_ylabel("Intensity I(q)")
            ax.legend()
            ax.grid(True)

            plt.savefig("bootstrapping_iteration_1.png", dpi=300)
            plt.close(fig)

    return np.array(bootstrap_results)

if __name__ == "__main__":
    import pandas as pd
    import os
    df = pd.read_csv(os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")), "20_06_2025_photoacids_SDS/P_50_S_500_high/P_50_S_500_high_0_00000_avg_filtered_subtracted_simple.dat"), sep='\s+', header=0)
    
    print(df.head())
    print(f"Data shape: {df.shape}")

    test_params = fit_data(df['q'], df['I'], initial_params=initial_params, fit_params=fit_params, method='lm')[0]
    all_params = {key: test_params[i] for i, key in enumerate([k for k in fit_params.keys() if fit_params[k]])}
    all_params.update({key: initial_params[key] for key in initial_params if key not in fit_params or not fit_params[key]})

    arr = residuals_bootstrap(df['q'], df['I'], all_params=all_params, fit_params=fit_params, n_iterations=20)
    
    ci = compute_confidence_intervals(arr)
    print(f"Confidence intervals: {ci}")

    import sys
    sys.exit(0)  # Exit early for testing purposes

    samples = bootstrapping(df['q'], df['I'], n_iterations=20, block_size=5)
    print(f"Generated {len(samples)} bootstrap samples.")
    fitted_params = fit_bootstrap_samples(samples, initial_params, fit_params)
    print(f"Fitted parameters from bootstrap samples: {fitted_params[:5]}")

    confidence_intervals = compute_confidence_intervals(fitted_params)
    print(f"Confidence intervals for fitted parameters: {confidence_intervals}")

    pd.DataFrame(confidence_intervals).to_csv("confidence_intervals.csv")

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.scatter(df['q'], df['I'], label='Data', color='blue', s=10)

    fig, ax = plt.subplots(figsize=(12, 8))

    param_names = list(fitted_params[0].keys())
    param_values = {name: [params[name] for params in fitted_params] for name in param_names}

    for i, param_name in enumerate(param_names):
        ax.plot(param_values[param_name], label=param_name, marker='o', linestyle='-', markersize=4)

    ax.set_title("Fitted Parameters from Bootstrap Samples")
    ax.set_xlabel("Bootstrap Sample Index")
    ax.set_ylabel("Parameter Value")
    ax.legend()
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig("fitted_parameters_bootstrap.png", dpi=300)