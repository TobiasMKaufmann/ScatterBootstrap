"""
This file extracts relevant data from .h5 files and creates different graphical and numerical representations.
"""

import pandas as pd
import matplotlib.pyplot as plt
import os
import numpy as np

folder = r"cluster/new_bootstrap_data"
files = [f for f in os.listdir(folder) if f.endswith('.h5')]
save_to_folder = "processed_data"

os.makedirs(save_to_folder, exist_ok=True)


# Store confidence intervals from all files
confidence_data = {}
    
for file in files:
    with pd.HDFStore(f'{folder}/{file}', 'r') as store:
        print(f"\n--- Processing {file} ---")
        confidence_intervals = store['confidence_intervals']
        print("DataFrame shape:", confidence_intervals.shape)
        print("DataFrame columns:", confidence_intervals.columns.tolist())
        print("DataFrame index:", confidence_intervals.index.tolist())
        print(confidence_intervals)
        
        label = file.replace('.h5', '')
        confidence_data[label] = confidence_intervals

print("\nConfidence data structure:")
for label, df in confidence_data.items():
    print(f"{label}: {df.shape}")

if confidence_data:
    first_dataset = list(confidence_data.values())[0]
    all_params = first_dataset.index.tolist()
    
    # Filter out parameters that are fixed (lower bound == upper bound)
    varying_params = []
    for param in all_params:
        for data in confidence_data.values():
            if param in data.index:
                lower = data.loc[param, 0]  # Column 0 = lower bound
                upper = data.loc[param, 1]  # Column 1 = upper bound
                if lower != upper:  # Parameter varies
                    varying_params.append(param)
                    break
    
    varying_params = list(set(varying_params))  # Remove duplicates
    
    if varying_params:
        fig, ax = plt.subplots(figsize=(14, 10))
        
        x_positions = np.arange(len(varying_params))
        width = 0.8 / len(confidence_data)  # Width for each dataset
        
        for i, (label, data) in enumerate(confidence_data.items()):
            means = []
            lower_errors = []
            upper_errors = []
            
            for param in varying_params:
                if param in data.index:
                    lower = data.loc[param, 0]  # Column 0 => lower bound
                    upper = data.loc[param, 1]  # Column 1 => upper bound
                    mean = (lower + upper) / 2
                    means.append(mean)
                    lower_errors.append(mean - lower)
                    upper_errors.append(upper - mean)
                else:
                    means.append(0)
                    lower_errors.append(0)
                    upper_errors.append(0)
            
            # Offset x positions for each dataset
            x_offset = x_positions + (i - len(confidence_data)/2 + 0.5) * width
            
            # Plot error bars
            ax.errorbar(x_offset, means, yerr=[lower_errors, upper_errors], 
                       label=label, marker='o', capsize=5, capthick=2, 
                       linewidth=2, markersize=6, fmt='o')
        
        ax.set_xlabel('Parameters')
        ax.set_ylabel('Parameter Values')
        ax.set_title('Confidence Intervals Comparison Across Datasets')
        ax.set_xticks(x_positions)
        ax.set_xticklabels(varying_params, rotation=45, ha='right')
        ax.set_ylim((0, 50))
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(rf'{save_to_folder}/confidence_intervals_comparison.png', dpi=300, bbox_inches='tight')
        plt.show()
        
        # Create grid of subplots - one for each parameter
        n_params = len(varying_params)
        n_cols = min(3, n_params)  # Max 3 columns
        n_rows = (n_params + n_cols - 1) // n_cols  # Calculate required rows
        
        fig_grid, axes = plt.subplots(n_rows, n_cols, figsize=(5*n_cols, 4*n_rows))
        if n_params == 1:
            axes = [axes]
        elif n_rows == 1:
            axes = axes.reshape(1, -1)
        axes = axes.flatten()
        
        for idx, param in enumerate(varying_params):
            ax = axes[idx]
            
            # Collect data for this parameter across all datasets
            dataset_names = []
            means = []
            lower_errors = []
            upper_errors = []
            
            for label, data in confidence_data.items():
                if param in data.index:
                    lower = data.loc[param, 0]
                    upper = data.loc[param, 1]
                    mean = (lower + upper) / 2
                    
                    dataset_names.append(label)
                    means.append(mean)
                    lower_errors.append(mean - lower)
                    upper_errors.append(upper - mean)
            
            # Plot error bars for this parameter
            x_pos = np.arange(len(dataset_names))
            ax.errorbar(x_pos, means, yerr=[lower_errors, upper_errors], 
                       marker='o', capsize=8, capthick=2, linewidth=2, 
                       markersize=8, fmt='o', color='blue')
            
            # Detect outliers and set y-limits if needed
            if means:
                all_values = means + [m + e for m, e in zip(means, upper_errors)] + [m - e for m, e in zip(means, lower_errors)]
                q75, q25 = np.percentile(all_values, [75, 25])
                iqr = q75 - q25
                outlier_threshold = q75 + 3 * iqr 
                
                max_val = max(all_values)
                min_val = min(all_values)
                
                # Only apply ylim if outlier is really extreme (more than 3 IQRs beyond Q3)
                if max_val > outlier_threshold and iqr > 0:
                    # Set upper limit to exclude extreme outliers but include reasonable variation
                    upper_limit = q75 + 2 * iqr
                    lower_limit = min(min_val * 0.95, q25 - 0.5 * iqr)
                    ax.set_ylim(lower_limit, upper_limit)
                    
                    # Add text annotation about clipped values
                    ax.text(0.02, 0.98, f'Clipped at {upper_limit:.3f}', 
                           transform=ax.transAxes, va='top', ha='left', 
                           bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.7),
                           fontsize=8)
            
            ax.set_title(f'{param}', fontsize=12, fontweight='bold')
            ax.set_xticks(x_pos)
            ax.set_xticklabels(dataset_names, rotation=45, ha='right')
            ax.grid(True, alpha=0.3)
            
            # Add value labels on the plot (only if not clipped)
            for i, (mean, lower_err, upper_err) in enumerate(zip(means, lower_errors, upper_errors)):
                y_text = mean + upper_err
                # Check if the text would be within the plot bounds
                if ax.get_ylim()[1] > y_text:
                    ax.text(i, y_text + (max(means) - min(means)) * 0.05, 
                           f'{mean:.3f}', ha='center', va='bottom', fontsize=8)
        
        # Hide unused subplots
        for idx in range(n_params, len(axes)):
            axes[idx].set_visible(False)
        
        plt.suptitle('Parameter Confidence Intervals by Dataset', fontsize=16, fontweight='bold')
        plt.tight_layout()
        plt.savefig(rf'{save_to_folder}/confidence_intervals_grid.png', dpi=300, bbox_inches='tight')
        plt.show()
        
        print(f"\nPlotted confidence intervals for {len(confidence_data)} datasets")
        print(f"Varying parameters: {varying_params}")
        print(f"Created grid plot with {n_rows}x{n_cols} subplots")
        
        # Create individual plots for each parameter
        print("\n--- Creating individual parameter plots ---")
        for param in varying_params:
            # Create folder for this parameter
            os.makedirs(param, exist_ok=True)
            
            # Create single plot for this parameter
            fig, ax = plt.subplots(figsize=(10, 6))
            
            # Collect data for this parameter across all datasets
            dataset_names = []
            means = []
            lower_errors = []
            upper_errors = []
            
            for label, data in confidence_data.items():
                if param in data.index:
                    lower = data.loc[param, 0]
                    upper = data.loc[param, 1]
                    mean = (lower + upper) / 2
                    
                    dataset_names.append(label)
                    means.append(mean)
                    lower_errors.append(mean - lower)
                    upper_errors.append(upper - mean)
            
            # Plot error bars for this parameter
            x_pos = np.arange(len(dataset_names))
            ax.errorbar(x_pos, means, yerr=[lower_errors, upper_errors], 
                       marker='o', capsize=8, capthick=2, linewidth=2, 
                       markersize=8, fmt='o', color='blue')
            
            # Detect outliers and set y-limits if needed
            if means:
                all_values = means + [m + e for m, e in zip(means, upper_errors)] + [m - e for m, e in zip(means, lower_errors)]
                q75, q25 = np.percentile(all_values, [75, 25])
                iqr = q75 - q25
                outlier_threshold = q75 + 3 * iqr 
                
                max_val = max(all_values)
                min_val = min(all_values)
                
                # Only apply ylim if outlier is really extreme
                if max_val > outlier_threshold and iqr > 0:
                    upper_limit = q75 + 2 * iqr
                    lower_limit = min(min_val * 0.95, q25 - 0.5 * iqr)
                    ax.set_ylim(lower_limit, upper_limit)
                    
                    # Add text annotation about clipped values
                    ax.text(0.02, 0.98, f'Clipped at {upper_limit:.3f}', 
                           transform=ax.transAxes, va='top', ha='left', 
                           bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.7),
                           fontsize=8)
            
            ax.set_title(f'{param}', fontsize=12, fontweight='bold')
            ax.set_xticks(x_pos)
            ax.set_xticklabels(dataset_names, rotation=45, ha='right')
            ax.grid(True, alpha=0.3)
            
            # Add value labels on the plot
            for i, (mean, lower_err, upper_err) in enumerate(zip(means, lower_errors, upper_errors)):
                y_text = mean + upper_err
                if ax.get_ylim()[1] > y_text:
                    ax.text(i, y_text + (max(means) - min(means)) * 0.05, 
                           f'{mean:.3f}', ha='center', va='bottom', fontsize=8)
            
            plt.tight_layout()
            plt.savefig(f'{save_to_folder}/{param}_confidence_intervals.png', dpi=300, bbox_inches='tight')
            plt.close()  # Close the figure to save memory

            print(f"Saved plot for {param} in folder '{save_to_folder}/'")

        print(f"\nCreated individual plots for {len(varying_params)} parameters")
        
        # Extract and plot all fitted parameters from bootstrap samples
        fitted_params_data = {}
        
        print("\n--- Extracting fitted parameters from bootstrap samples ---")
        for file in files:
            with pd.HDFStore(f'{folder}/{file}', 'r') as store:
                label = file.replace('.h5', '')
                
                # Find all fitted_params keys (e.g., fitted_params/s1, fitted_params/s2, etc.)
                fitted_keys = [k for k in store.keys() if k.startswith('/fitted_params/')]
                
                if fitted_keys:
                    print(f"Found {len(fitted_keys)} bootstrap samples for {label}")
                    
                    # Collect all fitted parameters for this dataset
                    all_fitted_params = []
                    for key in fitted_keys:
                        params_series = store[key]
                        all_fitted_params.append(params_series.to_dict())
                    
                    # Convert to DataFrame
                    fitted_df = pd.DataFrame(all_fitted_params)
                    fitted_params_data[label] = fitted_df
                    
                    print(f"Parameters shape for {label}: {fitted_df.shape}")
                    print(f"Parameters: {fitted_df.columns.tolist()}")
                        
        # Plot fitted parameters distributions
        if fitted_params_data:
            # Get all parameter names from the first dataset
            first_fitted_dataset = list(fitted_params_data.values())[0]
            all_fitted_params = first_fitted_dataset.columns.tolist()
            
            # Filter to only varying parameters (same as before)
            fitted_varying_params = [p for p in all_fitted_params if p in varying_params]
            
            if fitted_varying_params:
                # Create grid plot for fitted parameters distributions
                n_fitted_params = len(fitted_varying_params)
                n_cols_fitted = min(3, n_fitted_params)
                n_rows_fitted = (n_fitted_params + n_cols_fitted - 1) // n_cols_fitted
                
                fig_fitted, axes_fitted = plt.subplots(n_rows_fitted, n_cols_fitted, 
                                                      figsize=(5*n_cols_fitted, 4*n_rows_fitted))
                if n_fitted_params == 1:
                    axes_fitted = [axes_fitted]
                elif n_rows_fitted == 1:
                    axes_fitted = axes_fitted.reshape(1, -1)
                axes_fitted = axes_fitted.flatten()
                
                colors = plt.cm.Set1(np.linspace(0, 1, len(fitted_params_data)))
                
                for idx, param in enumerate(fitted_varying_params):
                    ax = axes_fitted[idx]
                    
                    for i, (label, fitted_df) in enumerate(fitted_params_data.items()):
                        if param in fitted_df.columns:
                            # Plot histogram/distribution of fitted values
                            values = fitted_df[param].dropna()
                            weights = np.ones_like(values) / len(values)  # Normalize to form a probability density
                            ax.hist(values, alpha=0.6, label=label, color=colors[i], 
                                   bins=min(20, len(values)//2), density=False, weights=weights)
                    
                    ax.set_title(f'{param} Distribution', fontsize=12, fontweight='bold')
                    ax.set_xlabel('Parameter Value')
                    ax.set_ylabel('Density')
                    ax.legend()
                    ax.grid(True, alpha=0.3)
                
                # Hide unused subplots
                for idx in range(n_fitted_params, len(axes_fitted)):
                    axes_fitted[idx].set_visible(False)
                
                plt.suptitle('Fitted Parameters Distributions from Bootstrap Samples', 
                           fontsize=16, fontweight='bold')
                plt.tight_layout()
                plt.savefig(rf'{save_to_folder}/fitted_parameters_distributions.png', dpi=300, bbox_inches='tight')
                plt.show()
                
                print(f"\nPlotted fitted parameters distributions for {len(fitted_params_data)} datasets")
                print(f"Fitted varying parameters: {fitted_varying_params}")
            else:
                print("No varying fitted parameters found to plot")


            # Just copy-paste from above to get individual plots for each dataset
            for dataset_label, current_fitted_dataset in fitted_params_data.items():
                
                print(f"\n--- Plotting fitted parameters distributions for {dataset_label} ---")
                all_fitted_params = current_fitted_dataset.columns.tolist()
                fitted_varying_params = [p for p in all_fitted_params if p in varying_params]

                n_fitted_params = len(fitted_varying_params)
                n_cols_fitted = min(3, n_fitted_params)
                n_rows_fitted = (n_fitted_params + n_cols_fitted - 1) // n_cols_fitted
                
                fig_fitted, axes_fitted = plt.subplots(n_rows_fitted, n_cols_fitted, 
                                                      figsize=(5*n_cols_fitted, 4*n_rows_fitted))
                if n_fitted_params == 1:
                    axes_fitted = [axes_fitted]
                elif n_rows_fitted == 1:
                    axes_fitted = axes_fitted.reshape(1, -1)
                axes_fitted = axes_fitted.flatten()
                
                for idx, param in enumerate(fitted_varying_params):
                    ax = axes_fitted[idx]
                    
                    if param in current_fitted_dataset.columns:
                        # Plot histogram/distribution of fitted values for current dataset only
                        values = current_fitted_dataset[param].dropna()
                        weights = np.ones_like(values) / len(values)  # Normalize to form a probability density
                        ax.hist(values, alpha=0.6, color='blue', 
                               bins=min(20, len(values)//2), density=False, weights=weights)
                    
                    ax.set_title(f'{param} Distribution', fontsize=12, fontweight='bold')
                    ax.set_xlabel('Parameter Value')
                    ax.set_ylabel('Density')
                    ax.grid(True, alpha=0.3)
                
                # Hide unused subplots
                for idx in range(n_fitted_params, len(axes_fitted)):
                    axes_fitted[idx].set_visible(False)
                
                plt.suptitle(f'Fitted Parameters Distributions - {dataset_label}', 
                           fontsize=16, fontweight='bold')
                plt.tight_layout()
                plt.savefig(rf'{save_to_folder}/fitted_parameters_distributions_{dataset_label}.png', dpi=300, bbox_inches='tight')
                plt.show()
                
                print(f"\nPlotted fitted parameters distributions for {len(fitted_params_data)} datasets")
                print(f"Fitted varying parameters: {fitted_varying_params}")
            else:
                print("No varying fitted parameters found to plot")
        else:
            print("No fitted parameters data found")
            
        # Create summary DataFrame with first fit parameters and confidence intervals using MultiIndex
        print("\n--- Creating summary DataFrame with MultiIndex ---")

        # TODO: THIS GIVES A HORRIBLE FORMAT!
        
        datasets = []
        parameters = set()
        data_dict = {}
        
        for file in files:
            with pd.HDFStore(f'{folder}/{file}', 'r') as store:
                label = file.replace('.h5', '')
                datasets.append(label)
                
                first_fit_params = store['first_fit_params']
                
                confidence_intervals = store['confidence_intervals']
                
                data_dict[label] = {}
                
                for param_name in first_fit_params.index:
                    parameters.add(param_name)
                    data_dict[label][param_name] = {
                        'Original_Fit': first_fit_params.loc[param_name],
                        'Lower_Bound': confidence_intervals.loc[param_name, 0] if param_name in confidence_intervals.index else None,
                        'Upper_Bound': confidence_intervals.loc[param_name, 1] if param_name in confidence_intervals.index else None
                    }
        
        # Create MultiIndex DataFrame
        parameters = sorted(list(parameters))
        
        # Create MultiIndex columns: (parameter, statistic)
        multi_columns = pd.MultiIndex.from_product([parameters, ['Original_Fit', 'Lower_Bound', 'Upper_Bound']], 
                                                  names=['Parameter', 'Statistic'])
        
        summary_df = pd.DataFrame(index=datasets, columns=multi_columns)
        
        for dataset in datasets:
            for param in parameters:
                if param in data_dict[dataset]:
                    summary_df.at[dataset, (param, 'Original_Fit')] = data_dict[dataset][param]['Original_Fit']
                    summary_df.at[dataset, (param, 'Lower_Bound')] = data_dict[dataset][param]['Lower_Bound']
                    summary_df.at[dataset, (param, 'Upper_Bound')] = data_dict[dataset][param]['Upper_Bound']
        
        print("\nSummary DataFrame with MultiIndex:")
        print(summary_df)
        
        # Save to CSV (MultiIndex format)
        summary_df.to_csv(rf'{save_to_folder}/parameter_summary_multiindex.csv')
        print(f"\nSaved summary to {save_to_folder}/parameter_summary_multiindex.csv")

    else:
        print("No varying parameters found to plot")
else:
    print("No confidence interval data found to plot")