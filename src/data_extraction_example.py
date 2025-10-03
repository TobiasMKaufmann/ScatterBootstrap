"""
Example usage of data extraction functions.
This file demonstrates how to import and use the data extraction functions
from a different Python file.
"""

# Import the data extraction functions
from data_extraction_functions import (
    load_confidence_intervals,
    identify_varying_parameters, 
    plot_confidence_intervals_comparison,
    plot_confidence_intervals_grid,
    create_individual_parameter_plots,
    load_fitted_parameters,
    plot_fitted_parameters_distributions,
    create_summary_dataframe,
    process_bootstrap_data  # Complete pipeline function
)

def example_usage():
    """Example of using data extraction functions step by step."""
    
    print("=== Data Extraction Functions Example ===\n")
    
    # Method 1: Use the complete pipeline (recommended for most users)
    print("Method 1: Complete Pipeline")
    print("-" * 30)
    
    results = process_bootstrap_data(
        folder_path='cluster/new_bootstrap_data',
        save_folder='my_analysis_results',
        create_plots=True,
        save_plots=True,
        show_plots=False  # Set to True to display plots
    )
    
    print(f"Pipeline processed {len(results.get('confidence_data', {}))} datasets")
    print(f"Found {len(results.get('varying_params', []))} varying parameters")
    print()
    
    # Method 2: Step-by-step processing (for custom workflows)
    print("Method 2: Step-by-step Processing")
    print("-" * 35)
    
    # Step 1: Load confidence intervals
    print("1. Loading confidence intervals...")
    confidence_data = load_confidence_intervals('cluster/new_bootstrap_data', verbose=False)
    print(f"   Loaded data for {len(confidence_data)} datasets")
    
    # Step 2: Identify varying parameters
    print("2. Identifying varying parameters...")
    varying_params = identify_varying_parameters(confidence_data)
    print(f"   Found {len(varying_params)} varying parameters: {varying_params}")
    
    # Step 3: Create specific plots
    if varying_params:
        print("3. Creating comparison plot...")
        fig_comparison = plot_confidence_intervals_comparison(
            confidence_data, 
            varying_params,
            save_path='my_analysis_results/custom_comparison.png',
            show_plot=False
        )
        
        print("4. Creating grid plot...")
        fig_grid = plot_confidence_intervals_grid(
            confidence_data,
            varying_params,
            save_path='my_analysis_results/custom_grid.png', 
            show_plot=False
        )
        
        print("5. Creating individual parameter plots...")
        individual_figs = create_individual_parameter_plots(
            confidence_data,
            varying_params,
            save_folder='my_analysis_results/individual_params'
        )
        print(f"   Created {len(individual_figs)} individual plots")
    
    # Step 4: Process fitted parameters
    print("6. Loading fitted parameters...")
    fitted_params_data = load_fitted_parameters('cluster/new_bootstrap_data', verbose=False)
    print(f"   Loaded fitted parameters for {len(fitted_params_data)} datasets")
    
    if fitted_params_data:
        print("7. Creating fitted parameter distributions...")
        fitted_figs = plot_fitted_parameters_distributions(
            fitted_params_data,
            varying_params,
            save_folder='my_analysis_results/fitted_distributions',
            show_plots=False
        )
        print(f"   Created distribution plots for {len(fitted_figs)} datasets")
    
    # Step 5: Create summary
    print("8. Creating summary DataFrame...")
    summary_df = create_summary_dataframe(
        'cluster/new_bootstrap_data',
        save_path='my_analysis_results/custom_summary.csv'
    )
    print(f"   Summary DataFrame shape: {summary_df.shape}")
    print()
    
    print("=== Analysis Complete ===")
    print("Check 'my_analysis_results/' folder for all outputs")
    
    return {
        'confidence_data': confidence_data,
        'varying_params': varying_params,
        'fitted_params_data': fitted_params_data,
        'summary_dataframe': summary_df
    }

def custom_analysis_example():
    """Example of custom analysis using the extracted data."""
    
    print("\n=== Custom Analysis Example ===\n")
    
    # Load only the data you need
    confidence_data = load_confidence_intervals('cluster/new_bootstrap_data', verbose=False)
    varying_params = identify_varying_parameters(confidence_data)
    
    print(f"Dataset names: {list(confidence_data.keys())}")
    print(f"Varying parameters: {varying_params}")
    
    # Custom analysis: Compare specific parameter across datasets
    if 'radius' in varying_params:
        print("\nCustom Analysis: Radius parameter across datasets")
        print("-" * 50)
        
        for dataset_name, data in confidence_data.items():
            if 'radius' in data.index:
                lower = data.loc['radius', 0]
                upper = data.loc['radius', 1]
                mean = (lower + upper) / 2
                uncertainty = (upper - lower) / 2
                print(f"{dataset_name:20s}: {mean:.3f} ± {uncertainty:.3f}")
    
    # Create a single custom plot
    if len(varying_params) >= 2:
        print(f"\nCreating custom plot for first 2 parameters: {varying_params[:2]}")
        fig = plot_confidence_intervals_comparison(
            confidence_data,
            varying_params[:2],  # Only first 2 parameters
            ylim=(0, 30),  # Custom y-axis range
            save_path='my_analysis_results/custom_two_params.png',
            show_plot=False
        )
        print("Custom plot saved!")

def minimal_example():
    """Minimal example for quick data extraction."""
    
    print("\n=== Minimal Example ===\n")
    
    # Just get the summary data quickly
    summary_df = create_summary_dataframe('cluster/new_bootstrap_data')
    
    print("Quick summary of all datasets:")
    print(summary_df.head())
    
    return summary_df

if __name__ == "__main__":
    # Run examples
    try:
        # Full example
        results = example_usage()
        
        # Custom analysis example 
        custom_analysis_example()
        
        # Minimal example
        minimal_results = minimal_example()
        
    except Exception as e:
        print(f"Error running examples: {e}")
        print("Make sure the 'cluster/new_bootstrap_data' folder exists with HDF5 files")
        print("You can modify the folder paths in the examples to match your data location.")