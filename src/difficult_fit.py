"""
This was another file used to find initial parameters for different data sets.
"""

from utils_old import fit_data, plot_fit_data
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


"""

Salt concentration higher for higher pH (see fits): of order 0.1 and 0.03 for lower pH (relevant for initial parameters)

"""

# The file to be examined:
file = "../../20_06_2025_photoacids_SDS/P_0_S_50_high/P_0_S_50_high_0_00000_avg_filtered_subtracted_simple.dat"

df = pd.read_csv(file, sep='\s+', header=0)


#plot_data(df["q"], df["I"], "raw_data")

# P_5_S_50_high
initial_params = {
    "scale": 1,
    "background": 0.001,
    "core_sld": 7.7,
    "shell_sld": 10.989,
    "solvent_sld": 9.4,
    "radius": 14.33,
    "thickness": 6.40,
    "length": 36.84,
    "radius_effective": 221.48,
    "vol_frac": 0.01, # Makes sense due to smaller concentration (about a factor of 10 different form the 500 mM)
    "zz": 26,
    "temp": 300,
    "csalt": 0.11,
    "dialec": 78.3
}

# P_0_S_50_med
initial_params = {
    "scale": 1,
    "background": 0.001,
    "core_sld": 7.7,
    "shell_sld": 10.989,
    "solvent_sld": 9.4,
    "radius": 14.34,
    "thickness": 6.40,
    "length": 36.79,
    "radius_effective": 149.40,
    "vol_frac": 0.01, # Makes sense due to smaller concentration (about a factor of 10 different form the 500 mM)
    "zz": 26,
    "temp": 300,
    "csalt": 0.03,
    "dialec": 78.3
}

# P_5_S_50_med NOT GOOD YET! Look at the fits in the plots
initial_params = {
    "scale": 1,
    "background": 0.001,
    "core_sld": 7.7,
    "shell_sld": 10.989,
    "solvent_sld": 9.4,
    "radius": 14.34,
    "thickness": 6.40,
    "length": 36.79,
    "radius_effective": 149.38,
    "vol_frac": 0.01,
    "zz": 26,
    "temp": 300,
    "csalt": 0.03,
    "dialec": 78.3
  }

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

# P_0_S_50_high
initial_params = {
    "scale": 1,
    "background": 0.001,
    "core_sld": 7.7,
    "shell_sld": 10.989,
    "solvent_sld": 9.4,
    "radius": 14.33,
    "thickness": 6.40,
    "length": 36.80,
    "radius_effective": 216.29,
    "vol_frac": 0.01, # Makes sense due to smaller concentration (about a factor of 10 different form the 500 mM)
    "zz": 26,
    "temp": 300,
    "csalt": 0.1100, # Makes sense due to higher pH
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

fitted_params, _, names_order = fit_data(df["q"], df["I"], initial_params, fit_params, bounds=bounds, method="trf")
fitted_dict = {name: fitted_params[i] for i, name in enumerate(names_order)}
print("Fitted parameters:")
for k, v in fitted_dict.items():
    print(f"  {k}: {v}")

total_dict = initial_params.copy()
total_dict.update(fitted_dict)

plot_fit_data(df["q"], df["I"], total_dict, "fit_data")