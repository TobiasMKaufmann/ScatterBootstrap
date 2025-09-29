# Cluster Processing for ECHEMES Bootstrapping

Workflow optimized for ETH HPC (Euler/Leonhard) using SLURM job scheduler.

## Files Overview

- `submit_job.sh` - SLURM job script for ETH HPC
- `setup_cluster.py` - Install dependencies and build C extensions  
- `process_data.py` - Run data.py equivalent (no plotting, just h5 generation)
- `collect_results.py` - Collect h5 files after processing
- `transfer.sh` - Transfer files to/from cluster with job submission
- `requirements_cluster.txt` - Minimal dependencies

## Workflow

### 1. Setup and Submit Job
```bash
# Edit transfer.sh with your NetHz ID first
./transfer.sh to
```

### 2. Monitor Job
```bash
# Check job status
./transfer.sh status

# View output (replace JOBID with actual job ID)
ssh your_nethz@euler.ethz.ch "cat echemes-bootstrapping/src/cluster/echemes_JOBID.out"
```

### 3. Collect Results
```bash
# Download results when job is complete
./transfer.sh from
```

## ETH HPC Specific Notes

- Uses SLURM job scheduler (`sbatch`, `squeue`)
- Loads required modules (gcc, python)
- Creates virtual environment on compute node
- Optimized resource allocation (4 CPUs, 8GB RAM, 4h runtime)
- Uses `rsync` for efficient file transfer

## Output

Creates h5 files in `bootstrap_data/` with:
- Raw experimental data (`raw_data`)
- Initial parameters (`initial_params`) 
- Fitted parameters (`first_fit_params`)
- Bootstrap samples (`fitted_params/s1-s100`, `synthetic_y/s1-s100`)
- Confidence intervals (`confidence_intervals`)
- Confidence intervals
- Synthetic data (`synthetic_y/s1`, `synthetic_y/s2`, etc.)

These are the same files that `data.py` creates locally, just without the plotting.