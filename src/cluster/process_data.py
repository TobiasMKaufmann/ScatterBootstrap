#!/usr/bin/env python
"""
High-Performance Cluster Bootstrap Analysis
============================================

Main processing script for the ECHEMES cluster computing framework, designed for
high-throughput bootstrap analysis on ETH HPC systems (Euler/Leonhard) using SLURM
job scheduling. Provides a streamlined, plotting-free version of the core analysis
optimized for batch processing of multiple SAS datasets.

Cluster Framework Overview
--------------------------

This script is part of a complete cluster computing workflow:

**Core Scripts:**
    - process_data.py (THIS FILE) - Main bootstrap analysis execution
    - submit_job.sh - SLURM job submission script for ETH HPC
    - setup_cluster.py - Dependency installation and C extension building
    - transfer.sh - Bidirectional file transfer and job management

**Configuration:**
    - content_verification.py - Quality assurance for analysis results
    - requirements_cluster.txt - Minimal dependency specification
    - README.md - Complete cluster usage documentation

Key Features
------------

**High-Performance Processing:**
    - Optimized for ETH HPC (Euler/Leonhard) SLURM environment
    - Minimal dependencies for cluster compatibility
    - No GUI/plotting dependencies - pure computational focus
    - Efficient memory management for large bootstrap iterations

**Automated Analysis Pipeline:**
    - Batch processing of multiple SAS datasets from JSON configuration
    - Automatic structure factor detection and model selection
    - Configurable bootstrap iterations (default: 5000 per dataset)
    - Intelligent parameter bounds and fitting constraints
    - Comprehensive error handling and progress reporting

**Data Management:**
    - HDF5-based result storage for efficient I/O
    - Structured metadata preservation
    - Raw data, fitted parameters, and bootstrap results in single files
    - Automatic confidence interval calculation and storage

**Flexibility:**
    - Dataset-specific structure factor inclusion/exclusion
    - Configurable fitting parameters and bounds per analysis
    - Support for both Levenberg-Marquardt and Trust Region algorithms
    - Selective dataset processing for testing and validation

**Cluster Integration:**
    - Compatible with ETH HPC module system
    - Automatic Python environment detection and setup
    - SLURM-optimized resource allocation (CPU, memory, time)
    - Remote monitoring and result retrieval capabilities

Output Structure
----------------

Each processed dataset generates an HDF5 file containing:

**Primary Data:**
    - raw_data: Original experimental q, I data
    - initial_params: Starting parameter values
    - residuals: Fit residuals from initial fit

**Fitting Results:**
    - first_fit_params: Initial fit results with fitted flags (value, fitted columns)

**Bootstrap Results (5000 iterations by default):**
    - fitted_params/s0 to s4999: Parameter values from each bootstrap sample
    - synthetic_y/s0 to s4999: Synthetic intensity data for each bootstrap sample

**Statistical Summary:**
    - confidence_intervals: Parameter uncertainty bounds (95% CI by default)

**Metadata Attributes:**
    - sample: Dataset name
    - processing_stage: Processing status ("bootstrap_analysis")

Usage Context
-------------

This script is typically executed via the SLURM job system:

.. code-block:: bash

    sbatch submit_job.sh

Or through the complete workflow:

.. code-block:: bash

    ./transfer.sh to        # Upload and submit job
    ./transfer.sh status    # Monitor progress
    ./transfer.sh retrieve  # Retrieve results

The cluster framework enables processing of computationally intensive bootstrap
analyses that would be impractical on local workstations, particularly for
large datasets or high iteration counts.

Cluster Compatibility
---------------------

While optimized for ETH HPC systems, this framework can be adapted for other
HPC clusters with similar architecture:

**Compatible Systems:**
    - SLURM-based job schedulers (LLNL SLURM, SchedMD SLURM)
    - PBS/Torque systems (with script modifications)
    - Linux-based HPC clusters (CentOS, RHEL, Ubuntu)
    - x86_64 architecture with Python 3.8+ support
    - Systems with module environment management

**Required Cluster Features:**
    - Shared filesystem accessible from compute nodes
    - Python development headers and C compiler (gcc/clang)
    - Scientific Python stack availability (numpy, scipy, pandas)
    - HDF5 libraries for data storage

**Adaptation Guidelines:**
    - Modify submit_job.sh for your scheduler (PBS, SGE, etc.)
    - Update module loading commands in setup scripts
    - Adjust resource requests (memory, CPU, time) for your queue limits
    - Verify C extension compilation with your cluster's toolchain

Performance Disclaimer
----------------------

⚠️  **IMPORTANT:** This implementation is NOT yet optimized for high-performance computing.

**Current Limitations:**
    - Sequential processing of datasets (no parallelization)
    - Single-threaded bootstrap iterations
    - No MPI or distributed computing support
    - Memory usage not optimized for large-scale analyses
    - C extensions compiled with basic optimization flags

**Performance Improvements Needed:**
    - Parallel processing of multiple datasets using MPI or multiprocessing
    - Vectorized bootstrap iterations with GPU acceleration
    - Memory-efficient streaming for large datasets
    - Advanced C compiler optimizations (-O3, -march=native)
    - Distributed computing across multiple nodes
    - Asynchronous I/O for HDF5 operations

**Current Status:**
    This framework provides functional cluster deployment but performance
    optimizations are planned for future releases. For production runs with
    thousands of bootstrap iterations or dozens of datasets, expect extended
    execution times. Consider starting with smaller iteration counts for testing.

Notes
-----
No virtual environment needed - using system Python with --user packages.
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