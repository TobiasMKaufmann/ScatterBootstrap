#!/bin/bash

# =============================================================================
# SLURM Job Submission Script for ScatterBootstrap Analysis
# =============================================================================
#
# This script handles automated job submission for the ScatterBootstrap
# framework on ETH HPC systems (Euler/Leonhard). It configures the SLURM
# environment, loads necessary Python modules, sets up dependencies, and
# executes the bootstrap analysis pipeline.
#
# SLURM Configuration:
# - 20 hours maximum runtime (adjust based on dataset size)
# - 8 CPU cores per task. The bootstrap refits run in parallel across these
#   cores (process_data.py reads $SLURM_CPUS_PER_TASK), so more cores = faster.
# - 2GB memory per CPU (suitable for moderate datasets)
# - Normal partition (adjust for priority/queue requirements)
#
# Process Flow:
# 1. Load ETH HPC Python environment modules
# 2. Detect and configure Python interpreter
# 3. Run setup_cluster.py for dependency installation
# 4. Execute process_data.py for bootstrap analysis
# 5. Optionally collect results (currently commented out)
#
#
# Monitoring:
# - Output: scatterbootstrap_%j.out (stdout and progress)
# - Errors: scatterbootstrap_%j.err (stderr and exceptions)
# - Job ID: %j placeholder replaced by SLURM
# =============================================================================

#SBATCH --job-name=scatterbootstrap
#SBATCH --output=scatterbootstrap_%j.out
#SBATCH --error=scatterbootstrap_%j.err
#SBATCH --time=20:00:00
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem-per-cpu=2G
#SBATCH --partition=normal

# The bootstrap parallelism uses one process per allocated core. Make the count
# visible to the analysis (process_data.py reads $SLURM_CPUS_PER_TASK).
echo "=== Allocated CPUs per task: ${SLURM_CPUS_PER_TASK:-unknown} ==="

# Load available Python module on ETH HPC
echo "=== Loading ETH HPC Python environment ==="
module load fast_python_workshop_cpu/2025.0.0 2>/dev/null && echo "✓ Loaded fast_python_workshop_cpu" || echo "✗ fast_python_workshop_cpu not found"

# Show what Python we're using after module load
echo "Python after module load: $(which python3 2>/dev/null || which python 2>/dev/null || echo 'not found')"
echo "Python version: $(python3 --version 2>/dev/null || python --version 2>/dev/null || echo 'not found')"

# Find Python interpreter
if command -v python3 &> /dev/null; then
    PYTHON=python3
elif command -v python &> /dev/null; then
    PYTHON=python
else
    echo "Error: No Python interpreter found"
    echo "Available interpreters:"
    ls -la /usr/bin/python* 2>/dev/null || echo "No python interpreters in /usr/bin"
    exit 1
fi

echo "Using Python interpreter: $PYTHON"
echo "Python version: $($PYTHON --version)"

# Setup environment
$PYTHON setup_cluster.py

# Run processing
$PYTHON process_data.py

# # Collect results
# $PYTHON collect_results.py