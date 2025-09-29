"""
Was used to check if the fits make sense (especially with respect to the given initial parameters).
"""

import pandas as pd
import os

def get_fitted_parameters_table(store_path):
    """
    Extract all fitted parameters from an HDF5 store and return as a DataFrame.
    
    store_path (str): Path to the HDF5 store file
        
    Returns:
    pd.DataFrame: DataFrame with parameters as columns and bootstrap samples as rows.
                    Includes a 'Sample' column with the sample number.
    """
    with pd.HDFStore(store_path, 'r') as store:
        # Find all fitted_params keys (fitted_params/s0, fitted_params/s1, etc.)
        fitted_keys = [k for k in store.keys() if k.startswith('/fitted_params/')]
        
        if not fitted_keys:
            return pd.DataFrame()
        
        # Sort keys by sample number
        fitted_keys.sort(key=lambda x: int(x.split('/s')[1]))
        
        # Collect all parameters
        all_params = []
        for key in fitted_keys:
            params = store[key].to_dict()
            sample_num = int(key.split('/s')[1])
            params['Sample'] = sample_num
            all_params.append(params)
        
        # Create DataFrame with Sample as first column
        df = pd.DataFrame(all_params)
        df = df[['Sample'] + [col for col in df.columns if col != 'Sample']]
        
        return df


def get_all_fitted_parameters_tables(folder_path="bootstrap_data"):
    """
    Extract fitted parameters from all HDF5 files in a folder.
    
    folder_path (str): Path to the folder containing HDF5 files
        
    Returns:
    dict: Dictionary mapping dataset names to their parameter DataFrames
    """
    if not os.path.exists(folder_path):
        return {}
    
    h5_files = [f for f in os.listdir(folder_path) if f.endswith('.h5')]
    
    all_dfs = {}
    for file in sorted(h5_files):
        file_path = os.path.join(folder_path, file)
        df = get_fitted_parameters_table(file_path)
        if not df.empty:
            dataset_name = file.replace('.h5', '').replace('bootstrap_results_', '')
            all_dfs[dataset_name] = df
    
    return all_dfs


def find_duplicate_values(df):
    """
    Find duplicate values in each column of a DataFrame.
    
    df (pd.DataFrame): DataFrame to check for duplicates
        
    Returns:
    dict: Dictionary mapping column names to their duplicate values and counts
    """
    duplicates = {}
    
    for column in df.columns:
        value_counts = df[column].value_counts()
        
        duplicate_values = value_counts[value_counts > 1]
        
        if len(duplicate_values) > 0:
            duplicates[column] = duplicate_values.to_dict()
    
    return duplicates
