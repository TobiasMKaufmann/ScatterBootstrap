"""
Fitted Parameters Table Utilities
==================================

Functions for extracting, analyzing, and validating fitted parameters from bootstrap
analysis results stored in HDF5 files. Helps verify parameter fit quality and
consistency across bootstrap samples.

Key Features
------------

**Parameter Extraction:**
    - Extract all fitted parameters from HDF5 bootstrap results
    - Automatic sample numbering and organization
    - Batch processing of multiple HDF5 files
    - Returns pandas DataFrames for easy analysis

**Quality Assurance:**
    - Identify duplicate parameter values across samples
    - Validate parameter consistency
    - Compare fitted values with initial estimates
    - Statistical summaries of parameter distributions

**Use Cases:**
    - Verify that bootstrap fitting is working correctly
    - Identify stuck or poorly converging parameters
    - Compare parameter distributions across datasets
    - Generate parameter summary reports

Functions
---------

**get_fitted_parameters_table(store_path):**
    Extract fitted parameters from a single HDF5 file.
    Returns DataFrame with samples as rows, parameters as columns.

**get_all_fitted_parameters_tables(folder_path):**
    Extract fitted parameters from all HDF5 files in a folder.
    Returns dictionary mapping dataset names to parameter DataFrames.

**find_duplicate_values(df):**
    Find duplicate values in each column of a DataFrame.
    Useful for identifying parameters that aren't varying across bootstrap samples.

Usage Examples
--------------

**Single File Analysis:**

.. code-block:: python

    from fitted_params_table import get_fitted_parameters_table
    
    # Extract parameters from one dataset
    params_df = get_fitted_parameters_table('bootstrap_data/P_5_S_500_med.h5')
    
    # View summary statistics
    print(params_df.describe())
    
    # Check for specific parameter
    radius_values = params_df['radius']
    print(f"Radius: {radius_values.mean():.2f} ± {radius_values.std():.2f}")

**Batch Processing:**

.. code-block:: python

    from fitted_params_table import get_all_fitted_parameters_tables
    
    # Process entire folder
    all_params = get_all_fitted_parameters_tables('bootstrap_data')
    
    # Analyze each dataset
    for dataset_name, params_df in all_params.items():
        print(f"\\n{dataset_name}:")
        print(params_df.describe())

**Quality Check:**

.. code-block:: python

    from fitted_params_table import (
        get_fitted_parameters_table,
        find_duplicate_values
    )
    
    # Load parameters
    params_df = get_fitted_parameters_table('bootstrap_data/P_5_S_500_med.h5')
    
    # Find stuck parameters (same value across many samples)
    duplicates = find_duplicate_values(params_df)
    
    if duplicates:
        print("Warning: Parameters with duplicate values detected!")
        for param, dup_dict in duplicates.items():
            print(f"  {param}: {len(dup_dict)} unique values repeated")
    else:
        print("All parameters varying correctly across samples")

Output Format
-------------

**Parameter DataFrame:**
    Columns: ['Sample', 'parameter1', 'parameter2', ...]
    Rows: Bootstrap sample numbers (0, 1, 2, ..., n_iterations-1)
    
**Duplicate Values Dictionary:**
    Format: {column_name: {value: count, ...}, ...}
    Only includes columns with duplicate values (count > 1)

Notes
-----
These utilities complement the data_extraction_functions module by providing
lower-level access to individual bootstrap samples rather than aggregated
confidence intervals.
"""

import pandas as pd
import os

def get_fitted_parameters_table(store_path):
    """
    Extract all fitted parameters from an HDF5 store and return as a DataFrame.
    
    Parameters
    ----------
    store_path : str
        Path to the HDF5 store file containing bootstrap results.
        
    Returns
    -------
    pandas.DataFrame
        DataFrame with parameters as columns and bootstrap samples as rows.
        Includes a 'Sample' column with the sample number as the first column.
        Returns empty DataFrame if no fitted_params keys found.
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
    
    Parameters
    ----------
    folder_path : str, optional
        Path to the folder containing HDF5 files. Default is "bootstrap_data".
        
    Returns
    -------
    dict
        Dictionary mapping dataset names to their parameter DataFrames.
        Keys are filenames without '.h5' extension. Returns empty dict if
        folder doesn't exist or contains no valid HDF5 files.
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
    
    Parameters
    ----------
    df : pandas.DataFrame
        DataFrame to check for duplicate values in each column.
        
    Returns
    -------
    dict
        Dictionary mapping column names to their duplicate values and counts.
        Only columns with duplicate values are included. Each value maps to
        a dict of {value: count} for values that appear more than once.
    """
    duplicates = {}
    
    for column in df.columns:
        value_counts = df[column].value_counts()
        
        duplicate_values = value_counts[value_counts > 1]
        
        if len(duplicate_values) > 0:
            duplicates[column] = duplicate_values.to_dict()
    
    return duplicates
