"""
Plot Comparisons Utility
=========================

Functionality for creating side-by-side visual comparisons between different fitting
results from bootstrap analysis. Particularly useful for validating improvements in
fitting algorithms or comparing results from different analysis runs.

Key Features
------------

**Data Loading:**
    - Load fitted parameters from HDF5 files
    - Extract raw experimental data automatically
    - Handle multiple datasets in batch mode
    - Graceful handling of missing datasets

**Model Configuration:**
    - Automatic structure factor detection
    - Parameter-based model selection
    - Support for form-factor-only analyses
    - Flexible parameter handling

**Visualization:**
    - Side-by-side comparison images
    - Individual fit plots for old and new results
    - High-quality output with customizable resolution
    - Organized naming scheme for easy identification
    - Automatic cleanup of temporary files

**Batch Processing:**
    - Process entire folders of HDF5 files
    - Match corresponding old/new datasets
    - Handle missing comparisons gracefully
    - Generate comprehensive comparison sets

Workflow
--------

1. Loads fitted parameters and experimental data from HDF5 stores
2. Determines appropriate model settings (structure factor usage)
3. Generates individual fit plots using plotting utilities
4. Combines plots side-by-side for easy visual comparison
5. Saves comparison images with organized naming scheme
6. Cleans up temporary files automatically

Use Cases
---------

**Algorithm Validation:**
    Compare results before and after algorithm improvements to verify that
    changes produce better fits without introducing artifacts.

**Quality Assurance:**
    Generate comparison plots for all datasets to quickly identify which
    analyses improved and which may need manual review.

**Publication Figures:**
    Create publication-ready comparison figures showing improvement in
    fitting quality across multiple datasets.

**Troubleshooting:**
    Identify systematic issues by comparing successful and problematic fits
    side-by-side to understand failure modes.

Functions
---------

**load_h5_datasets(base_folder):**
    Load all HDF5 files from a folder and extract fitted parameters and raw data.
    Returns dictionary with dataset names as keys.

**determine_structure_factor(params_dict):**
    Check parameter dictionary to determine if structure factor should be used.
    Returns boolean indicating structure factor availability.

**create_comparison_plots_from_h5(new_folder, old_folder, output_folder):**
    Main function to create side-by-side comparison plots from two sets of
    HDF5 analysis results.

Usage Example
-------------

**Basic Comparison:**

.. code-block:: python

    from plot_comparisons import create_comparison_plots_from_h5
    
    # Compare new analysis results against baseline
    create_comparison_plots_from_h5(
        new_folder='cluster/new_bootstrap_data',
        old_folder='cluster/old_bootstrap_data',
        output_folder='comparison_plots'
    )

**Custom Configuration:**

.. code-block:: python

    from plot_comparisons import (
        load_h5_datasets,
        determine_structure_factor,
        create_comparison_plots_from_h5
    )
    
    # Load specific datasets
    new_data = load_h5_datasets('new_results')
    old_data = load_h5_datasets('old_results')
    
    # Check what datasets are available
    common_datasets = set(new_data.keys()) & set(old_data.keys())
    print(f"Found {len(common_datasets)} datasets for comparison")
    
    # Generate comparisons
    create_comparison_plots_from_h5('new_results', 'old_results')

Output Format
-------------

**Comparison Images:**
    - Format: PNG with 300 DPI
    - Layout: Two panels side-by-side (old left, new right)
    - Naming: comparison_{dataset_name}.png
    - Location: Specified output folder

**Individual Plots:**
    - Temporary plots created during processing
    - Automatically cleaned up after combination
    - Can be preserved by modifying cleanup code

Notes
-----
This module uses scatterbootstrap.plot_fit_data to generate the individual
fit plots, so the FORM_FACTOR_MODEL / STRUCTURE_FACTOR_MODEL below must match
the models used to produce the HDF5 files being compared (see
src/cluster/process_data.py).

The module uses PIL (Pillow) for image manipulation to create side-by-side
comparisons from individual plot files. Install it with `pip install Pillow`.
"""

import pandas as pd
import numpy as np
import os
from scatterbootstrap import plot_fit_data
from PIL import Image

# Folder to save results to:
folder = "fit_results"

# Models used to produce the HDF5 files being compared (see src/cluster/process_data.py)
FORM_FACTOR_MODEL = "core_shell_cylinder"
STRUCTURE_FACTOR_MODEL = "hayter_msa"

def load_h5_datasets(base_folder):
    """
    Load all datasets from HDF5 files in the specified folder.
    
    Parameters
    ----------
    base_folder : str
        Path to folder containing HDF5 (.h5) files with bootstrap results.
    
    Returns
    -------
    dict
        Dictionary with dataset names as keys and tuples as values.
        Each tuple contains (params_dict, q_data, I_data) where:
        - params_dict : dict of fitted parameter values
        - q_data : numpy.ndarray of scattering vector values
        - I_data : numpy.ndarray of intensity values
    """
    datasets = {}
    
    if not os.path.exists(base_folder):
        print(f"Folder {base_folder} does not exist")
        return datasets
    
    h5_files = [f for f in os.listdir(base_folder) if f.endswith('.h5')]
    print(f"Found {len(h5_files)} H5 files in {base_folder}")
    
    for h5_file in h5_files:
        dataset_name = h5_file.replace('.h5', '')
        h5_path = os.path.join(base_folder, h5_file)
        
        try:
            with pd.HDFStore(h5_path, mode='r') as store:
                # Raw data
                raw_data = store['raw_data']
                q_data = raw_data['q'].values
                I_data = raw_data['I'].values
                
                # Fitted parameters
                first_fit_params = store['first_fit_params']
                
                params_dict = {}
                for param_name in first_fit_params.index:
                    params_dict[param_name] = first_fit_params.loc[param_name, 'value']
                
                datasets[dataset_name] = (params_dict, q_data, I_data)
                print(f"Loaded {dataset_name}: {len(params_dict)} parameters, {len(q_data)} data points")
                
        except Exception as e:
            print(f"Error loading {h5_file}: {e}")
    
    return datasets

def determine_structure_factor(params_dict):
    """
    Determine if structure factor should be used based on available parameters.
    
    Parameters
    ----------
    params_dict : dict
        Parameter dictionary containing fitted or initial parameter values.
    
    Returns
    -------
    bool
        True if all structure factor parameters (radius_effective, volfraction,
        charge, temperature, saltconc, dielectconst) are present and not None,
        False otherwise.
    """
    # Structure factor parameters needed
    sf_params = ['radius_effective', 'volfraction', 'charge', 'temperature', 'saltconc', 'dielectconst']
    
    # Check if all structure factor parameters are present and not None
    has_all_sf_params = all(param in params_dict and params_dict[param] is not None for param in sf_params)
    
    return has_all_sf_params

def create_comparison_plots_from_h5(new_folder, old_folder, output_folder=None):
    """
    Create side-by-side comparison plots from old and new HDF5 analysis results.
    
    This function loads fitted parameters and raw data from two sets of HDF5 files,
    generates individual fit plots for each, and combines them side-by-side for
    easy visual comparison of analysis improvements.
    
    Parameters
    ----------
    new_folder : str
        Path to folder containing new/updated HDF5 files with bootstrap results.
    old_folder : str
        Path to folder containing old/baseline HDF5 files for comparison.
    output_folder : str, optional
        Folder path to save the comparison plots. If None, uses the module-level
        'folder' variable. Default is None.
    
    Returns
    -------
    None
        Generates and saves comparison plot images to the specified output folder.
    """
    
    if output_folder is None:
        output_folder = folder
    
    print("Loading new datasets...")
    new_datasets = load_h5_datasets(new_folder)
    
    print("Loading old datasets...")
    old_datasets = load_h5_datasets(old_folder)
    
    all_dataset_names = set(new_datasets.keys()).union(set(old_datasets.keys()))
    
    if len(all_dataset_names) == 0:
        print("No datasets found")
        return
    
    print(f"Creating comparison plots for {len(all_dataset_names)} datasets...")
    
    temp_folder = os.path.join(output_folder, "temp_plots")
    comparison_folder = os.path.join(output_folder, "comparisons")
    
    os.makedirs(temp_folder, exist_ok=True)
    os.makedirs(comparison_folder, exist_ok=True)
    
    for dataset_name in sorted(all_dataset_names):
        print(f"Processing {dataset_name}...")
        
        safe_name = dataset_name.replace('/', '_').replace(' ', '_')
        
        # Generate old fit plot
        old_plot_path = None
        if dataset_name in old_datasets:
            params_dict, q_data, I_data = old_datasets[dataset_name]
            structure_factor = determine_structure_factor(params_dict)
            
            print(f"  Old {dataset_name}: {len(params_dict)} params, structure_factor={structure_factor}")
            
            try:
                old_title = f"{dataset_name} - Old Fit"
                plot_fit_data(q_data, I_data, params_dict,
                            form_factor_model=FORM_FACTOR_MODEL,
                            structure_factor_model=STRUCTURE_FACTOR_MODEL if structure_factor else None,
                            title=old_title,
                            folder=temp_folder)
                
                expected_old_filename = f"{old_title.replace(' ', '_').lower()}.png"
                old_plot_path = os.path.join(temp_folder, expected_old_filename)
                
            except Exception as e:
                print(f"  Error creating old fit plot for {dataset_name}: {e}")
        
        # Generate new fit plot  
        new_plot_path = None
        if dataset_name in new_datasets:
            params_dict, q_data, I_data = new_datasets[dataset_name]
            structure_factor = determine_structure_factor(params_dict)
            
            print(f"  New {dataset_name}: {len(params_dict)} params, structure_factor={structure_factor}")
            
            try:
                new_title = f"{dataset_name} - New Fit"
                plot_fit_data(q_data, I_data, params_dict,
                            form_factor_model=FORM_FACTOR_MODEL,
                            structure_factor_model=STRUCTURE_FACTOR_MODEL if structure_factor else None,
                            title=new_title,
                            folder=temp_folder)
                
                expected_new_filename = f"{new_title.replace(' ', '_').lower()}.png"
                new_plot_path = os.path.join(temp_folder, expected_new_filename)
                
            except Exception as e:
                print(f"  Error creating new fit plot for {dataset_name}: {e}")
        
        # Combine images side by side
        if old_plot_path and os.path.exists(old_plot_path) and new_plot_path and os.path.exists(new_plot_path):
            try:
                # Load images
                old_img = Image.open(old_plot_path)
                new_img = Image.open(new_plot_path)
                
                # Create combined image
                total_width = old_img.width + new_img.width
                max_height = max(old_img.height, new_img.height)
                combined_img = Image.new('RGB', (total_width, max_height), 'white')
                
                # Paste images side by side
                combined_img.paste(old_img, (0, 0))
                combined_img.paste(new_img, (old_img.width, 0))
                
                # Save combined image
                comparison_path = os.path.join(comparison_folder, f"{safe_name}_comparison.png")
                combined_img.save(comparison_path, dpi=(300, 300))
                print(f"  Saved comparison: {comparison_path}")
                
            except Exception as e:
                print(f"  Error combining images for {dataset_name}: {e}")
        
        elif old_plot_path and os.path.exists(old_plot_path):
            # Only old plot available
            old_img = Image.open(old_plot_path)
            comparison_path = os.path.join(comparison_folder, f"{safe_name}_old_only.png")
            old_img.save(comparison_path)
            print(f"  Saved old-only plot: {comparison_path}")
            
        elif new_plot_path and os.path.exists(new_plot_path):
            # Only new plot available  
            new_img = Image.open(new_plot_path)
            comparison_path = os.path.join(comparison_folder, f"{safe_name}_new_only.png")
            new_img.save(comparison_path)
            print(f"  Saved new-only plot: {comparison_path}")
    
    print(f"All comparison plots saved to: {comparison_folder}")
    
    # Clean up temporary files
    try:
        import shutil
        shutil.rmtree(temp_folder)
        print("Temporary files cleaned up")
    except Exception as e:
        print(f"Warning: Could not clean up temp folder: {e}")