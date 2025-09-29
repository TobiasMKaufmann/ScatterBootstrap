"""
To check if what was returned actually makes sense.
"""

import pandas as pd
import sys
sys.path.append('..')
from utils_old import plot_fit_data

which = "P_5_S_50_med.h5"

with pd.HDFStore(f"bootstrap_data/bootstrap_data/{which}") as store:
    fitted_keys = [k for k in store.keys() if k.startswith('/fitted_params/')]
    print(f"\nFound {len(fitted_keys)} fitted_params keys")
    
    if fitted_keys:
        first_key = fitted_keys[0]
        params_series = store[first_key]
        print(f"\nFirst key: {first_key}")
        print(f"Available parameters: {params_series.index.tolist()}")
        
        column_name = "thickness"  # Change this to the parameter you want
        all_values = []
        
        for key in fitted_keys:
            params_series = store[key]
            if column_name in params_series.index:
                all_values.append(params_series[column_name])
        
        # Get unique values and count
        # if all_values:
        #     unique_values = pd.Series(all_values).nunique()
        #     print(f"\nNumber of unique values for '{column_name}': {unique_values}")
        #     print(f"Unique values: {sorted(pd.Series(all_values).unique())}")
        # else:
        #     print(f"\nNo values found for parameter '{column_name}'")
    
    print("\nPlotting original fit...")
    
    raw_data = store['raw_data']
    first_fit_params = store['first_fit_params']
    
    params_dict = {}
    for param_name in first_fit_params.index:
        params_dict[param_name] = first_fit_params.loc[param_name, 'value']

    print(params_dict)
    
    plot_fit_data(raw_data['q'], raw_data['I'], params_dict, 
                  title=f"Original Fit - {which.replace('.h5', '')}", 
                  structure_factor=False)
    
    print(f"Plot saved as original_fit_-_{which.replace('.h5', '')}.png")
    