"""
This file was used to find initial parameters to fit the low concentration data sets without a structure factor.
"""

from utils_old import fit_data, plot_fit_data
import numpy as np
import pandas as pd 
import matplotlib.pyplot as plt

fit_params = {
    "scale": True,
    "background": True,
    "core_sld": False,
    "shell_sld": False,
    "solvent_sld": False,
    "radius": True,
    "thickness": True,
    "length": True,
}

bounds = {
    "scale": (0, np.inf),
    "background": (0, np.inf),
    "core_sld": (0, np.inf),
    "shell_sld": (0, np.inf),
    "solvent_sld": (0, np.inf),
    "radius": (11, 18),
    "thickness": (5.5, 7),
    "length": (25, 50),
}

initial_params_550med = {
    "background":0.001,
    "core_sld":7.7,
    "length":30,
    "radius":12,
    "scale":1,
    "shell_sld":10.989,
    "solvent_sld":9.4,
    "thickness":7,
}

initial_params_550high = {
    "background":0.001,
    "core_sld":7.7,
    "length":40,
    "radius":16,
    "scale":1,
    "shell_sld":10.989,
    "solvent_sld":9.4,
    "thickness":5.989531,
}

df = pd.read_csv(r"20_06_2025_photoacids_SDS/P_5_S_50_med/P_5_S_50_med_0_00000_avg_filtered_subtracted_simple.dat", sep='\s+', header=0)

df.plot(x="q", y="I")
plt.savefig("diff_data.png", dpi=300)

ps, cov, param_order = fit_data(df["q"], df["I"], initial_params=initial_params_550med, fit_params=fit_params, bounds=bounds, method="trf", structure_factor=False)

fitted_params = dict(zip(param_order, ps))
fitted_params.update({k: initial_params_550med[k] for k in initial_params_550med if k not in param_order})
print(fitted_params)

plot_fit_data(df["q"], df["I"], fitted_params, title="TEST_FIT_NEW_NO_SF", structure_factor=False)