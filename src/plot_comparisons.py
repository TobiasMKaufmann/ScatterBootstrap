import pandas as pd
import numpy as np
import os
from utils_old import plot_fit_data
from PIL import Image

# Folder to save results to:
folder = "fit_results"

def load_h5_datasets(base_folder):
    """
    Load all datasets from H5 files in the specified folder.
    
    base_folder (str): Path to folder containing .h5 files
    
    Returns:
    dict: Dictionary with dataset names as keys and (params_dict, q_data, I_data) as values
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
    
    params_dict (dict): Parameter dictionary
    
    Returns:
    bool: True if structure factor parameters are available
    """
    # Structure factor parameters needed
    sf_params = ['radius_effective', 'vol_frac', 'zz', 'temp', 'csalt', 'dialec']
    
    # Check if all structure factor parameters are present and not None
    has_all_sf_params = all(param in params_dict and params_dict[param] is not None for param in sf_params)
    
    return has_all_sf_params

def create_comparison_plots_from_h5(new_folder, old_folder, output_folder=None):
    """
    Create side-by-side comparison plots using H5 data and plot_fit_data.
    
    Parameters:
    new_folder (str): Path to folder with new H5 files
    old_folder (str): Path to folder with old H5 files  
    output_folder (str): Folder to save the plots
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
                            title=old_title,
                            folder=temp_folder,
                            structure_factor=structure_factor)
                
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
                            title=new_title,
                            folder=temp_folder,
                            structure_factor=structure_factor)
                
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

# Generate comparison plots using H5 data
print("Creating comparison plots from H5 files...")
new_h5_folder = "cluster/new_bootstrap_data"
old_h5_folder = "cluster/old_data/bootstrap_data"

create_comparison_plots_from_h5(new_h5_folder, old_h5_folder, folder)

print("Comparison plots completed!")