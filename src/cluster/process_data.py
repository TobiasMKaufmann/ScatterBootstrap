#!/usr/bin/env python
"""
Cluster version of data.py - no plotting, optimized for batch processing
"""
import sys
import os
sys.path.append('..')
sys.path.append('../core_shell_cylinder')

# No virtual environment needed - using system Python with --user packages

import json
import glob
import pandas as pd
import numpy as np
try:
    from utils import fit_data, residuals_bootstrap, compute_confidence_intervals
    print("Successfully imported utils functions")
except ImportError as e:
    print(f"Error importing utils: {e}")
    print("This might be due to missing dependencies or C extension issues")
    sys.exit(1)

def main():
    rel_file = "avg_filtered_subtracted_simple"
    
    # Load parameters
    with open("../initial_params.json", "r") as f:
        params = json.load(f)
    
    fit_params = {
        "scale": True,
        "background": True,
        "core_sld": False,
        "shell_sld": False,
        "solvent_sld": False,
        "radius": True,
        "thickness": True,
        "length": True,
        "radius_effective": False,
        "vol_frac": True,
        "zz": True,
        "temp": False,
        "csalt": True,
        "dialec": False
    }

    fit_params_no_sf = {
        "scale": True,
        "background": True,
        "core_sld": False,
        "shell_sld": False,
        "solvent_sld": False,
        "radius": True,
        "thickness": True,
        "length": True,
    }

    # Change as needed
    bounds = {
        "scale": (0, np.inf),
        "background": (0, np.inf),
        "core_sld": (0, np.inf),
        "shell_sld": (0, np.inf),
        "solvent_sld": (0, np.inf),
        "radius": (11, 18),
        "thickness": (5.5, 7),
        "length": (25, 50),
        # "radius_effective": (0, 500),
        # "vol_frac": (0.0, 1),
        # "zz": (0, 100),
        # "temp": (273, 373),
        # "csalt": (0, 0.5),
        # "dialec": (1, np.inf)
    }


    structure_factors_to_exclude = ["P_5_S_50_med", "P_0_S_50_high", "P_5_S_50_high"]

    
    original_fit_params = fit_params.copy()
    
    # Create output directory
    if not os.path.isdir("bootstrap_data"):
        os.makedirs("bootstrap_data")
    
    # Process each dataset
    for which, d in params.items():
        if which in structure_factors_to_exclude:
            structure_factor = False
            fit_params = fit_params_no_sf.copy()
        else:
            structure_factor = True
            fit_params = original_fit_params.copy()

        if which != "P_5_S_50_med":
            continue  # For testing, process only one dataset

        print(f"Processing {which}...")
        
        # Set missing parameters
        for k in d:
            if d[k] is None:
                fit_params[k] = False
                d[k] = 0
        
        # Find data file
        data_pattern = f"../20_06_2025_photoacids_SDS/{which}/*_{rel_file}.dat"
        files = glob.glob(data_pattern)
        
        if not files:
            print(f"Warning: No data file found for {which}")
            continue
            
        file = pd.read_csv(files[0], sep='\s+', header=0)
        
        # Remove existing HDF5 file
        h5_file = f"bootstrap_data/{which}.h5"
        if os.path.exists(h5_file):
            os.remove(h5_file)
        
        try:
            with pd.HDFStore(h5_file, "w") as store:
                # Store raw data and parameters
                store.put('raw_data', file)
                store.put('initial_params', pd.Series(d))
                
                # Add file metadata
                store.root._v_attrs.sample = which
                store.root._v_attrs.processing_stage = "bootstrap_analysis"
                

                # Perform initial fit
                print(f"  Initial fit...")
                if structure_factor:
                    print("  Using structure factor")
                    first_fit, covariance, names = fit_data(file["q"], file["I"], 
                                                            initial_params=d, fit_params=fit_params, method="lm", 
                                                            structure_factor=structure_factor)
                elif not structure_factor:
                    print("  Not using structure factor")
                    first_fit, covariance, names = fit_data(file["q"], file["I"], 
                                                            initial_params=d, fit_params=fit_params, method="trf", 
                                                            structure_factor=structure_factor, bounds=bounds)
                # new_initial_params = {name: val for name, val in zip(names, first_fit)}
                # new_initial_params.update({name: val for name, val in d.items if not fit_params[name]})
                
                # Create first_fit_params DataFrame
                first_fit_params_data = []
                new_initial_params = {}
                for param_name in fit_params.keys():
                    if fit_params[param_name] and param_name in names:
                        idx = names.index(param_name)
                        value = first_fit[idx]
                        fitted = True

                        new_initial_params[param_name] = value
                    else:
                        value = d.get(param_name, 0)
                        fitted = False

                        new_initial_params[param_name] = value
                    
                    first_fit_params_data.append({'value': value, 'fitted': fitted})
                
                first_fit_params_df = pd.DataFrame(first_fit_params_data, 
                                                 index=list(fit_params.keys()))
                store.put('first_fit_params', first_fit_params_df)
                
                print(f"  Bootstrap analysis...")
                if structure_factor:
                    print("  Using structure factor")
                    bootstrap_results = residuals_bootstrap(file["q"], file["I"], new_initial_params, fit_params, 
                                                            n_iterations=5000, store=store, method="lm", 
                                                            structure_factor=structure_factor)
                elif not structure_factor:
                    print("  Not using structure factor")
                    bootstrap_results = residuals_bootstrap(file["q"], file["I"], new_initial_params, fit_params, 
                                                            n_iterations=5000, store=store, method="trf", 
                                                            structure_factor=structure_factor, bounds=bounds)

                print(f"  Computing confidence intervals...")
                confidence_intervals = compute_confidence_intervals(bootstrap_results)
                store.put('confidence_intervals', pd.DataFrame(confidence_intervals).T)
                
            print(f"  Completed {which}")
            
        except Exception as e:
            print(f"Error processing {which}: {e}")
            continue
        
        # Reset fit_params for next iteration
        fit_params = original_fit_params.copy()
    
    print(f"Processing complete! All samples processed.")

if __name__ == "__main__":
    main()