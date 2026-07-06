#!/usr/bin/env python
"""
High-Performance Cluster Bootstrap Analysis
============================================

Main processing script for the ScatterBootstrap cluster computing framework, designed for
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

Configuration
-------------

**CRITICAL:** Before running, configure these global variables at the top of the script:

**Data Location:**

.. code-block:: python

    DATASET_FOLDER = "FOLDER"  # Main folder with subfolders
    REL_FILE_IDENTIFIER = "IDENTIFIER"  # File suffix

**Fitting Parameters:**

.. code-block:: python

    FIT_PARAMS_WITH_SF = {...}  # Parameters to fit with structure factor
    FIT_PARAMS_NO_SF = {...}    # Parameters to fit without structure factor
    PARAMETER_BOUNDS_WITH_SF = {...}   # Bounds when using structure factor
    PARAMETER_BOUNDS_NO_SF = {...}     # Bounds when not using structure factor
    STRUCTURE_FACTORS_TO_EXCLUDE = [...]  # Samples without structure factor

**Fitting Methods:**

.. code-block:: python

    FITTING_METHOD_WITH_SF = "lm"   # Method when using structure factor
    FITTING_METHOD_NO_SF = "trf"    # Method without structure factor
    N_BOOTSTRAP_ITERATIONS = 5000   # Number of bootstrap samples

**Required Data Structure:**

.. code-block:: text

    DATASET_FOLDER/
      ├── sample1/
      │   └── sample1_{REL_FILE_IDENTIFIER}.dat
      ├── sample2/
      │   └── sample2_{REL_FILE_IDENTIFIER}.dat
      └── sample3/
          └── sample3_{REL_FILE_IDENTIFIER}.dat

**Requirements:**
    - All data files MUST have .dat extension
    - Files MUST be in whitespace-separated format with headers
    - Each sample has its own subfolder named after the sample
    - File naming: {sample_name}_{REL_FILE_IDENTIFIER}.dat
    - Review ALL fitting parameters and adjust for your specific system
    - Set appropriate parameter bounds based on expected physical values
    - Choose fitting methods compatible with your constraints

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

Performance
-----------

The bootstrap refits are run **in parallel** across worker processes (see the
``N_JOBS`` configuration variable below and the ``n_jobs`` argument of
``residuals_bootstrap``). By default ``N_JOBS`` reads SLURM's
``$SLURM_CPUS_PER_TASK``, so the analysis uses exactly the cores you allocate in
``submit_job.sh`` (``--cpus-per-task``); locally it falls back to all available
cores. This gives a near-linear speedup with the number of cores.

**Current scope:**
    - Datasets are still processed one after another (the parallelism is within
      a dataset's bootstrap, which is where the cost is).
    - No multi-node/MPI distribution (single node, many cores).

**Possible future improvements:**
    - Distributing whole datasets across nodes (e.g. a SLURM job array).
    - Advanced C compiler optimizations (-O3, -march=native).
    - Asynchronous I/O for HDF5 operations.

To scale across many datasets, submit one job per dataset (a SLURM array) and
let each job parallelize its own bootstrap over its allocated cores.

Notes
-----
No virtual environment needed - using system Python with --user packages.
"""

import os

# No virtual environment needed - using system Python with --user packages

import json
import glob
import pandas as pd
import numpy as np

from scatterbootstrap import fit_data, residuals_bootstrap, compute_confidence_intervals

# ============================================================================
# GLOBAL CONFIGURATION - MODIFY THESE TO MATCH YOUR DATA STRUCTURE AND ANALYSIS
# ============================================================================

# -----------------------------------------------------------------------------
# MODEL SELECTION
# -----------------------------------------------------------------------------

# Form factor and structure factor models, by name (see
# scatterbootstrap.list_form_factor_models() / list_structure_factor_models()
# for all available options). These determine which parameters
# initial_params.json, FIT_PARAMS_*, and PARAMETER_BOUNDS_* must provide.
FORM_FACTOR_MODEL = "core_shell_cylinder"
STRUCTURE_FACTOR_MODEL = "hayter_msa"

# -----------------------------------------------------------------------------
# DATA LOCATION CONFIGURATION
# -----------------------------------------------------------------------------

# Main dataset folder containing subfolders for each sample
DATASET_FOLDER = "FOLDER_WITH_SUBFOLDERS"  # Change this to your data folder

# File identifier suffix (must be .dat files)
# Files should be named: {sample_name}_{REL_FILE_IDENTIFIER}.dat
REL_FILE_IDENTIFIER = "IDENTIFIER"  # Change this to your file identifier

# Data structure should be organized as:
# DATASET_FOLDER/
#   ├── sample1/
#   │   └── sample1_identifier.dat
#   ├── sample2/
#   │   └── sample2_identifier.dat
#   └── ...

# -----------------------------------------------------------------------------
# FITTING CONFIGURATION - ADJUST FOR YOUR SPECIFIC ANALYSIS
# -----------------------------------------------------------------------------

# NOTE: Configure FORM_FACTOR_MODEL / STRUCTURE_FACTOR_MODEL above before running this script!

# ⚠️  IMPORTANT: Review and modify these settings based on your data!
#
# These parameters control which parameters are fitted vs fixed, parameter bounds,
# fitting methods, and structure factor usage. The default values are examples
# and should be adjusted for your specific samples.

# Parameters to fit when using structure factor (True = fit, False = fixed)
FIT_PARAMS_WITH_SF = {
    "scale": True,
    "background": True,
    "core_sld": False,
    "shell_sld": False,
    "solvent_sld": False,
    "radius": True,
    "thickness": True,
    "length": True,
    "radius_effective": False,
    "volfraction": True,
    "charge": True,
    "temperature": False,
    "saltconc": True,
    "dielectconst": False
}

# Parameters to fit without structure factor (form factor only)
FIT_PARAMS_NO_SF = {
    "scale": True,
    "background": True,
    "core_sld": False,
    "shell_sld": False,
    "solvent_sld": False,
    "radius": True,
    "thickness": True,
    "length": True,
}

# Parameter bounds for WITH structure factor (if using trf/dogbox methods)
# Only used if FITTING_METHOD_WITH_SF is set to "trf" or "dogbox"
PARAMETER_BOUNDS_WITH_SF = {
    "scale": (0, np.inf),
    "background": (0, np.inf),
    "core_sld": (0, np.inf),
    "shell_sld": (0, np.inf),
    "solvent_sld": (0, np.inf),
    "radius": (11, 18),          # ⚠️  Adjust for your particle size!
    "thickness": (5.5, 7),        # ⚠️  Adjust for your shell thickness!
    "length": (25, 50),           # ⚠️  Adjust for your cylinder length!
    # Structure factor parameters (if fitted):
    "radius_effective": (0, 500),
    "volfraction": (0.0, 1),
    "charge": (0, 100),
    "temperature": (273, 373),
    "saltconc": (0, 0.5),
    "dielectconst": (1, np.inf)
}

# Parameter bounds for WITHOUT structure factor (typically used with trf/dogbox)
# Adjust ranges for your system!
PARAMETER_BOUNDS_NO_SF = {
    "scale": (0, np.inf),
    "background": (0, np.inf),
    "core_sld": (0, np.inf),
    "shell_sld": (0, np.inf),
    "solvent_sld": (0, np.inf),
    "radius": (11, 18),          # ⚠️  Adjust for your particle size!
    "thickness": (5.5, 7),        # ⚠️  Adjust for your shell thickness!
    "length": (25, 50),           # ⚠️  Adjust for your cylinder length!
}

# Datasets to exclude from structure factor calculations
# List sample names that should be fitted without structure factor
STRUCTURE_FACTORS_TO_EXCLUDE = ["dataset1", "dataset2"]  # ⚠️  Replace with your sample names!

# -----------------------------------------------------------------------------
# FITTING METHOD CONFIGURATION
# -----------------------------------------------------------------------------

# ⚠️  CRITICAL: Choose appropriate fitting methods for your data!
#
# Two fitting scenarios are defined:
# 1. WITH structure factor: Uses Levenberg-Marquardt ("lm") - unbounded optimization
# 2. WITHOUT structure factor: Uses Trust Region Reflective ("trf") - supports bounds
#
# Available methods: "lm" (Levenberg-Marquardt), "trf" (Trust Region), "dogbox"
# 
# To change methods, modify the if/elif blocks in the fitting sections below:
#   - Search for: method="lm" and method="trf"
#   - Change to your preferred method
#   - Add/remove bounds parameter as needed (lm doesn't support bounds)

FITTING_METHOD_WITH_SF = "lm"      # ⚠️  Method when using structure factor
FITTING_METHOD_NO_SF = "trf"       # ⚠️  Method without structure factor (supports bounds)

# Number of bootstrap iterations (higher = better statistics, longer runtime)
N_BOOTSTRAP_ITERATIONS = 5000      # ⚠️  Adjust based on desired precision vs compute time

# Number of parallel worker processes for the bootstrap refits. The bootstrap
# iterations are independent, so this gives a near-linear speedup. On SLURM this
# automatically uses the cores you allocated via --cpus-per-task; locally it
# falls back to "-1" (all available cores). Set to 1 to force serial execution.
N_JOBS = int(os.environ.get("SLURM_CPUS_PER_TASK", 0)) or -1

# ============================================================================

def main():
    """
    Main processing function for cluster bootstrap analysis.
    
    ⚠️  BEFORE RUNNING: Ensure all global configuration variables are set!
    
    This function:
    1. Loads initial parameters from initial_params.json
    2. Processes each dataset using configured fitting parameters
    3. Determines structure factor usage per dataset
    4. Performs initial fit with configured method
    5. Runs bootstrap analysis with configured iterations
    6. Saves results to HDF5 files in bootstrap_data/
    
    Configuration is controlled by global variables at top of script.
    See documentation header for detailed configuration instructions.
    """
    # Load parameters from initial_params.json
    with open("../initial_params.json", "r") as f:
        params = json.load(f)
    
    # Use global configuration variables
    fit_params = FIT_PARAMS_WITH_SF.copy()
    fit_params_no_sf = FIT_PARAMS_NO_SF.copy()
    bounds_with_sf = PARAMETER_BOUNDS_WITH_SF.copy()
    bounds_no_sf = PARAMETER_BOUNDS_NO_SF.copy()
    structure_factors_to_exclude = STRUCTURE_FACTORS_TO_EXCLUDE
    
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

        print(f"Processing {which}...")
        
        # Set missing parameters
        for k in d:
            if d[k] is None:
                fit_params[k] = False
                d[k] = 0
        
        # Find data file
        data_pattern = f"{DATASET_FOLDER}/{which}/*_{REL_FILE_IDENTIFIER}.dat"
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
                # ⚠️  FITTING METHOD CONFIGURATION:
                # To change fitting method or bounds, modify the global variables:
                # - FITTING_METHOD_WITH_SF and PARAMETER_BOUNDS_WITH_SF
                # - FITTING_METHOD_NO_SF and PARAMETER_BOUNDS_NO_SF
                sf_model = STRUCTURE_FACTOR_MODEL if structure_factor else None

                print(f"  Initial fit...")
                if structure_factor:
                    print(f"  Using structure factor (method: {FITTING_METHOD_WITH_SF})")
                    first_fit, covariance, names = fit_data(file["q"], file["I"], FORM_FACTOR_MODEL, sf_model,
                                                            initial_params=d, fit_params=fit_params,
                                                            method=FITTING_METHOD_WITH_SF, bounds=bounds_with_sf)
                else:
                    print(f"  Not using structure factor (method: {FITTING_METHOD_NO_SF})")
                    first_fit, covariance, names = fit_data(file["q"], file["I"], FORM_FACTOR_MODEL, sf_model,
                                                            initial_params=d, fit_params=fit_params,
                                                            method=FITTING_METHOD_NO_SF, bounds=bounds_no_sf)
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
                
                # Bootstrap analysis
                # ⚠️  BOOTSTRAP CONFIGURATION:
                # Number of iterations: N_BOOTSTRAP_ITERATIONS (currently: {N_BOOTSTRAP_ITERATIONS})
                # Fitting methods and bounds same as initial fit (see global variables)
                print(f"  Bootstrap analysis ({N_BOOTSTRAP_ITERATIONS} iterations, "
                      f"n_jobs={N_JOBS})...")
                if structure_factor:
                    print(f"  Using structure factor (method: {FITTING_METHOD_WITH_SF})")
                    bootstrap_results = residuals_bootstrap(file["q"], file["I"], FORM_FACTOR_MODEL, sf_model,
                                                            all_params=new_initial_params, fit_params=fit_params,
                                                            n_iterations=N_BOOTSTRAP_ITERATIONS, store=store,
                                                            method=FITTING_METHOD_WITH_SF, bounds=bounds_with_sf,
                                                            n_jobs=N_JOBS)
                else:
                    print(f"  Not using structure factor (method: {FITTING_METHOD_NO_SF})")
                    bootstrap_results = residuals_bootstrap(file["q"], file["I"], FORM_FACTOR_MODEL, sf_model,
                                                            all_params=new_initial_params, fit_params=fit_params,
                                                            n_iterations=N_BOOTSTRAP_ITERATIONS, store=store,
                                                            method=FITTING_METHOD_NO_SF, bounds=bounds_no_sf,
                                                            n_jobs=N_JOBS)

                print(f"  Computing confidence intervals...")
                confidence_intervals = compute_confidence_intervals(bootstrap_results, confidence_level=0.95)
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
