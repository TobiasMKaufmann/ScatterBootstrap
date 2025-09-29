"""
This file was used for testing the bootstrapping and safely storing all of the relecant data.
"""

import os
import json
import glob
import pandas as pd
import numpy as np
from utils_old import fit_data, plot_fit_data, residuals_bootstrap, compute_confidence_intervals

# This is the unique identification to identify the relevant .dat file containing the data set (in the file name):
rel_file = "avg_filtered_subtracted_simple"

with open("initial_params.json", "r") as f:
    params = json.load(f)


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


# with pd.HDFStore("bootstrap_data/P_0_S_500_high.h5") as store:
#     raw_data = store['raw_data']
#     initial_params = store['initial_params']
#     first_fit_params = store['first_fit_params']
#     confidence_intervals = store['confidence_intervals']
#     res = store['synthetic_y/s1']
#     fit = store['fitted_params/s1']


original_fit_params = fit_params.copy()

if not os.path.isdir("bootstrap_data"):
    os.makedirs("bootstrap_data")


# Change as needed
bounds = {
    "scale": (0, np.inf),
    "background": (0, np.inf),
    "core_sld": (0, np.inf),
    "shell_sld": (0, np.inf),
    "solvent_sld": (0, np.inf),
    "radius": (12, 15),
    "thickness": (6, 7),
    "length": (30, 40),
    "radius_effective": (0, 500),
    "vol_frac": (0.0, 1),
    "zz": (0, 100),
    "temp": (273, 373),
    "csalt": (0, 0.5),
    "dialec": (1, np.inf)
}

for which, d in params.items():

    # d = {k: (26 if k == 'zz' and v is None else (0.05 if k == 'csalt' and v is None else (v if v is not None else 0))) for k, v in d.items()}
    for k in d:
        if d[k] is None:
            fit_params[k] = False
            d[k] = 0
    returned = glob.glob(rf"../../20_06_2025_photoacids_SDS/{which}/*_{rel_file}.dat")[0]
    file = pd.read_csv(returned, sep='\s+', header=0)

    # Remove existing HDF5 file if it exists
    h5_file = f"bootstrap_data/{which}.h5"
    if os.path.exists(h5_file):
        os.remove(h5_file)

    with pd.HDFStore(h5_file, "w") as store:
        store.put('raw_data', file)
        store.put('initial_params', pd.Series(d))

        first_fit, _, names = fit_data(file["q"], file["I"], initial_params=d, fit_params=fit_params, method="lm")
        first_params = {key: first_fit[i] for i, key in enumerate([k for k in fit_params.keys() if fit_params[k]])}
        first_params.update({key: d[key] for key in d.keys() if key not in fit_params or not fit_params[key]})

        params_df = pd.DataFrame({
            'value': [first_params[key] for key in fit_params.keys()],
            'fitted': [fit_params[key] for key in fit_params.keys()]
        }, index=list(fit_params.keys()))
        
        store.put('first_fit_params', params_df)

        plot_fit_data(file["q"], file["I"], first_params, title=which)

        fit_params = original_fit_params

        residuals = residuals_bootstrap(file["q"], file["I"], first_params, fit_params, n_iterations=1000, store=store, method="trf")    
        ci = compute_confidence_intervals(residuals)
        print(f"Confidence intervals for {which}: {ci}")

        store.put('confidence_intervals', pd.DataFrame(ci).T)
