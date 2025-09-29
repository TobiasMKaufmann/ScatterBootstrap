#!/bin/bash
#SBATCH --job-name=echemes_bootstrap
#SBATCH --output=echemes_%j.out
#SBATCH --error=echemes_%j.err
#SBATCH --time=20:00:00
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem-per-cpu=2G
#SBATCH --partition=normal

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

# Collect results
$PYTHON collect_results.py