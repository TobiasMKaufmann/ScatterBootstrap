# Cluster Processing for ECHEMES Bootstrapping

Comprehensive workflow for ETH HPC (Euler/Leonhard) using SLURM job scheduler.
Optimized for high-throughput bootstrap analysis of small-angle scattering data.

## Files Overview

### Core Scripts:
- **`process_data.py`** - Main bootstrap analysis script (no plotting, HDF5 output only)
- **`submit_job.sh`** - SLURM job submission script with resource allocation
- **`setup_cluster.py`** - Automatic dependency installation and C extension building
- **`transfer.sh`** - Comprehensive file transfer and job management tool

### Configuration:
- **`requirements_cluster.txt`** - Minimal Python dependencies for cluster
- **`initial_params.json`** - Parameter configurations (in parent directory)

### Documentation:
- **`README.md`** - This file

**Note:** The `old/` directory contains deprecated files and is excluded from transfers.

## Data Structure Requirements

**CRITICAL:** Before running the analysis, ensure your data follows this structure:

### Required Directory Layout:
```
DATASET_FOLDER/                    # Main folder
  ├── sample1/                     # Subfolder for each dataset
  │   └── sample1_IDENTIFIER.dat
  ├── sample2/
  │   └── sample2_IDENTIFIER.dat
  └── sample3/
      └── sample3_IDENTIFIER.dat
```

### File Requirements:
- **File Extension:** All data files MUST be `.dat` files
- **File Format:** Whitespace-separated columns with headers (typically: `q`, `I`, `dI`)
- **Naming Convention:** `{sample_name}_{REL_FILE_IDENTIFIER}.dat`
- **Organization:** Each sample must have its own subfolder named after the sample

### Configuration in process_data.py:

Edit these global variables at the top of `process_data.py`:

```python
# Main dataset folder containing subfolders for each sample
DATASET_FOLDER = "FOLDER"

# File identifier suffix (must be .dat files)
REL_FILE_IDENTIFIER = "IDENTIFIER"
```

**Example:** If your sample is named `P_5_S_50_high` and your `REL_FILE_IDENTIFIER` is `avg_filtered_subtracted_simple`, the script will look for:
```
../20_06_2025_photoacids_SDS/P_5_S_50_high/P_5_S_50_high_0_00000_avg_filtered_subtracted_simple.dat
```

## Quick Start Workflow

### 1. Initial Setup
```bash
# Edit transfer.sh with your NetHz credentials
nano transfer.sh
# Set: CLUSTER_USER="your_nethz"

# Configure data paths in process_data.py
nano process_data.py
# Set: DATASET_FOLDER and REL_FILE_IDENTIFIER
```

### 2. Upload and Submit Job
```bash
./transfer.sh to
```
This will:
- Transfer all necessary files to cluster (excluding old/, *.h5, *.so, etc.)
- Submit SLURM job automatically
- Return job ID for monitoring

### 3. Monitor Progress
```bash
# Check job status in queue
./transfer.sh status

# Comprehensive check (status + logs + output files)
./transfer.sh check

# View available log files
./transfer.sh logs

# View specific job log (replace 12345 with actual job ID)
./transfer.sh viewlog 12345
```

### 4. Download Results (PRIMARY METHOD)
```bash
./transfer.sh retrieve
```
This will:
- Check for completed HDF5 files
- Create timestamped archive
- Download archive to local directory
- Extract results to `bootstrap_data/`

## Available Commands

### Core Workflow:
- **`to`** - Upload files and submit SLURM job
- **`retrieve`** - Download results (PRIMARY METHOD, recommended)
- **`from`** - Download results (deprecated, use retrieve)

### Testing & Verification:
- **`test`** - Upload files and run setup verification only

### Monitoring:
- **`status`** - Check SLURM job queue status
- **`check`** - Comprehensive status (jobs + logs + files)
- **`logs`** - List available job log files
- **`viewlog JOBID`** - View specific job's output and error logs

### Maintenance:
- **`clean`** - Remove temporary files from cluster
- **`list`** - List all files on cluster
- **`delete`** - Delete ALL files from cluster (requires confirmation)

## ETH HPC Configuration

### SLURM Resource Allocation:
- **Runtime**: 20 hours (adjustable in submit_job.sh)
- **CPUs**: 4 cores per task
- **Memory**: 2GB per CPU (8GB total)
- **Partition**: normal (standard priority)

### Recommendations for Large Datasets:
- Increase time limit: `--time=48:00:00`
- Increase memory: `--mem-per-cpu=4G`
- Monitor resource usage in job logs

### Module System:
- Automatically loads `fast_python_workshop_cpu/2025.0.0`
- Falls back to system Python if module unavailable
- Uses user-space pip installations (`--user` flag)

## Output Files

Each processed dataset generates an HDF5 file in `bootstrap_data/` containing:

### Data Structure:

**Primary Data:**
- **`raw_data`** - Original experimental data (pandas DataFrame)
  - Columns: `q` (scattering vector), `I` (intensity)
  
- **`initial_params`** - Starting parameter values (pandas Series)
  - All form factor and structure factor parameters
  - Used as initial guesses for fitting

**Fitting Results:**
- **`first_fit_params`** - Initial fit results (pandas DataFrame)
  - Columns: `value` (fitted/fixed values), `fitted` (boolean flag)
  - Index: parameter names
  - Distinguishes between fitted and fixed parameters
  
- **`residuals`** - Fit residuals from initial fit (pandas Series)
  - Calculated as: `y_data - fitted_y`
  - Used for bootstrap resampling

**Bootstrap Results (5000 iterations by default):**
- **`fitted_params/s0` to `s4999`** - Parameter values from each bootstrap sample
  - Each stored as pandas Series with parameter names as index
  - Contains fitted parameters after resampling residuals
  
- **`synthetic_y/s0` to `s4999`** - Synthetic intensity data for each bootstrap sample
  - Each stored as pandas Series
  - Generated by adding resampled residuals to original data

**Statistical Summary:**
- **`confidence_intervals`** - Parameter uncertainty bounds (pandas DataFrame)
  - Default: 95% confidence intervals (α = 0.05)
  - Calculated from bootstrap distribution percentiles
  - Format: `[p*(B·α/2), p*(B·(1-α/2))]` where B = number of bootstrap samples

**Metadata Attributes:**
- **`sample`** - Dataset name (e.g., "P_5_S_500_med")
- **`processing_stage`** - Processing status ("bootstrap_analysis")

### File Naming:
- Format: `{dataset_name}.h5`
- Example: `P_5_S_500_med.h5`

### Accessing Data:
```python
import pandas as pd

with pd.HDFStore('bootstrap_data/P_5_S_500_med.h5', 'r') as store:
    # Load original data
    raw_data = store['raw_data']
    
    # Load fit results
    first_fit = store['first_fit_params']
    confidence_intervals = store['confidence_intervals']
    
    # Load bootstrap samples
    bootstrap_params = [store[f'fitted_params/s{i}'] for i in range(5000)]
    
    # Access metadata
    sample_name = store.root._v_attrs.sample
```

## Performance Notes

⚠️ **Current Status**: Functional but not yet optimized for high-performance computing.

### Current Limitations:
- Sequential processing of datasets (no parallelization)
- Single-threaded bootstrap iterations
- No MPI or distributed computing support

### Typical Runtime:
- Small dataset (1000 bootstrap): ~1-2 hours
- Standard dataset (5000 bootstrap): ~4-8 hours
- Large dataset (10000 bootstrap): ~12-20 hours

### Planned Optimizations:
- Parallel processing of multiple datasets
- Vectorized bootstrap iterations
- Advanced compiler optimizations
- GPU acceleration support

## Troubleshooting

### Job Fails Immediately:
```bash
# Check setup and system info
./transfer.sh test

# View error log
./transfer.sh logs
./transfer.sh viewlog JOBID
```

### No Output Files:
```bash
# Check if job completed
./transfer.sh status

# Check for h5 files on cluster
./transfer.sh check

# View processing logs
./transfer.sh viewlog JOBID
```

### Import Errors:
- C extensions are automatically recompiled on cluster
- Check `setup_cluster.py` output in job logs
- Verify Python version compatibility (requires 3.8+)

### Module Not Found:
- ETH HPC modules may change
- Script automatically falls back to system Python
- Check which Python is used in job output

## File Transfer Details

### Automatically Excluded:
- `*.h5` - HDF5 files (regenerated on cluster)
- `*.png` - Plot files (not needed for computation)
- `*.tar.gz` - Archives (to reduce transfer size)
- `*.so` - Compiled libraries (recompiled for cluster architecture)
- `old/`, `*/old/` - Deprecated files and directories
- `.git/` - Git repository (version control not needed)
- `__pycache__/` - Python cache (regenerated)

### Transfer Methods:
- **Primary**: rsync (efficient, incremental)
- **Fallback**: scp (if rsync unavailable)
- **Direction**: Bidirectional (to/from cluster)

## Remote Access

### Direct SSH:
```bash
# Connect to cluster
ssh your_nethz@euler.ethz.ch

# Navigate to project
cd echemes-bootstrapping/src/cluster

# Check files
ls -la bootstrap_data/
```

### Manual Job Submission:
```bash
ssh your_nethz@euler.ethz.ch
cd echemes-bootstrapping/src/cluster
sbatch submit_job.sh
```

## Data Analysis

After downloading results with `./transfer.sh retrieve`:

1. Results are in `./bootstrap_data/` directory
2. Use `data_extraction_functions.py` for analysis
3. Generate plots and confidence intervals
4. Create summary reports

See main project README.md for analysis tools and examples.

---

**Author**: Tobias Kaufmann  
**Project**: ECHEMES Bootstrapping - Advanced SAS Analysis Tools  
**Cluster**: ETH HPC (Euler/Leonhard Open)  
**License**: MIT