#!/bin/bash

# =============================================================================
# ETH HPC Cluster Transfer and Job Management Script
# =============================================================================
#
# This script provides comprehensive file transfer, job submission, and monitoring
# capabilities for the ECHEMES bootstrapping framework on ETH HPC systems
# (Euler/Leonhard). It handles bidirectional file synchronization, automated
# job submission via SLURM, and remote monitoring of analysis progress.
#
# Key Features:
# - Intelligent file transfer with rsync/scp fallback
# - Automatic exclusion of large files, build artifacts, and old folders
# - SLURM job submission and status monitoring
# - Remote log file viewing and result collection
# - Comprehensive cleanup and maintenance commands
# - Support for both Euler and Leonhard clusters
#
# Available Commands:
# ==================
#
# Core Workflow:
#   to              Upload files to cluster and submit SLURM job
#   retrieve        Download results (PRIMARY METHOD - recommended)
#   from            Download results (deprecated, use retrieve instead)
#
# Testing & Verification:
#   test            Upload files and run setup verification
#
# Monitoring:
#   status          Check SLURM job queue status
#   check           Comprehensive status check (jobs, logs, output files)
#   logs            List available job log files
#   viewlog JOBID   View specific job's output and error logs
#
# Maintenance:
#   clean           Remove temporary files from cluster (h5, png, cache)
#   list            List all files on cluster
#   delete          Delete ALL files from cluster (with confirmation)
#
# Usage Examples:
# ==============
#   # Basic workflow
#   ./transfer.sh to                    # Upload and start analysis
#   ./transfer.sh status                # Check if job is running
#   ./transfer.sh check                 # Comprehensive status check
#   ./transfer.sh retrieve              # Download completed results
#
#   # Monitoring and debugging
#   ./transfer.sh logs                  # List available log files
#   ./transfer.sh viewlog 12345         # View logs for job 12345
#   ./transfer.sh list                  # See all cluster files
#
#   # Testing and cleanup
#   ./transfer.sh test                  # Test environment setup
#   ./transfer.sh clean                 # Remove temporary files
#
# File Exclusions:
# - HDF5 files (*.h5) - regenerated on cluster
# - Plots (*.png) - not needed for computation
# - Archives (*.tar.gz) - reduce transfer size
# - Compiled libraries (*.so) - recompiled for cluster architecture
# - Old folders (old/, */old/) - deprecated files
# - Git repository (.git/) - version control not needed
# - Python cache (__pycache__/) - regenerated
#
# Prerequisites:
# - SSH key-based authentication to ETH HPC
# - rsync or scp available locally
# - Proper NetHz credentials configured
# - CLUSTER_USER variable set below
#
# Configuration:
# Edit the following variables before first use:
#   CLUSTER_USER="your_nethz"          # Your NetHz username
#   CLUSTER_HOST="euler.ethz.ch"       # or "leonhard.ethz.ch"
#   REMOTE_DIR="echemes-bootstrapping"  # Remote directory name
# =============================================================================

# Configuration - EDIT THESE
CLUSTER_USER=""
CLUSTER_HOST="euler.ethz.ch"  # or "leonhard.ethz.ch"
LOCAL_DIR="../"
REMOTE_DIR="echemes-bootstrapping"

case "$1" in
    "to")
        echo "Transferring files to ETH HPC..."
        
        # Create remote directory first
        echo "Creating remote directory..."
        ssh ${CLUSTER_USER}@${CLUSTER_HOST} "mkdir -p ${REMOTE_DIR}"
        
        # Try rsync first, fall back to scp if rsync not available
        if command -v rsync >/dev/null 2>&1; then
            # Go up two levels to transfer the entire project structure
            cd ../..
            rsync -avz --exclude='*.h5' --exclude='__pycache__' --exclude='*.png' --exclude='*.tar.gz' \
                --exclude='old/' --exclude='*/old/' --exclude='.git/' --exclude='*.so' \
                --exclude='venv/' --exclude='env/' --exclude='.venv/' \
                --exclude='site-packages/' --exclude='*/site-packages/' \
                --exclude='*/test_*.py' --exclude='test_*.py' \
                --exclude='*/tests/' --exclude='tests/' \
                . ${CLUSTER_USER}@${CLUSTER_HOST}:${REMOTE_DIR}/
            cd - > /dev/null
        else
            echo "rsync not found, using scp..."
            # Create temporary directory with proper structure
            TEMP_DIR=$(mktemp -d)
            echo "Creating filtered copy in ${TEMP_DIR}..."
            # Go up two levels and copy entire project
            cd ../..
            cp -r . ${TEMP_DIR}/project
            cd - > /dev/null
            # Remove excluded files
            find ${TEMP_DIR} -name "*.h5" -delete
            find ${TEMP_DIR} -name "*.png" -delete
            find ${TEMP_DIR} -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
            find ${TEMP_DIR} -name "*.pyc" -delete
            find ${TEMP_DIR} -name "*.tar.gz" -delete
            find ${TEMP_DIR} -name "*.so" -delete
            find ${TEMP_DIR} -name "old" -type d -exec rm -rf {} + 2>/dev/null || true
            find ${TEMP_DIR} -name ".git" -type d -exec rm -rf {} + 2>/dev/null || true
            find ${TEMP_DIR} -name "venv" -type d -exec rm -rf {} + 2>/dev/null || true
            find ${TEMP_DIR} -name "env" -type d -exec rm -rf {} + 2>/dev/null || true
            find ${TEMP_DIR} -name ".venv" -type d -exec rm -rf {} + 2>/dev/null || true
            find ${TEMP_DIR} -name "site-packages" -type d -exec rm -rf {} + 2>/dev/null || true
            find ${TEMP_DIR} -name "test_*.py" -delete
            find ${TEMP_DIR} -name "tests" -type d -exec rm -rf {} + 2>/dev/null || true
            # Transfer the entire project structure
            scp -r ${TEMP_DIR}/project/* ${CLUSTER_USER}@${CLUSTER_HOST}:${REMOTE_DIR}/
            # Clean up
            rm -rf ${TEMP_DIR}
        fi
        
        echo "Submitting job..."
        ssh ${CLUSTER_USER}@${CLUSTER_HOST} \
            "module load rsync 2>/dev/null || true; cd ${REMOTE_DIR}/src/cluster && sbatch submit_job.sh"
        ;;
    "test")
        echo "Transferring files to ETH HPC for testing (including precompiled .so files)..."
        
        # Create remote directory first
        echo "Creating remote directory..."
        ssh ${CLUSTER_USER}@${CLUSTER_HOST} "mkdir -p ${REMOTE_DIR}"
        
        # Try rsync first, fall back to scp if rsync not available
        # For test command, include .so files (precompiled extensions)
        if command -v rsync >/dev/null 2>&1; then
            # Go up two levels to transfer the entire project structure
            cd ../..
            rsync -avz --exclude='*.h5' --exclude='__pycache__' --exclude='*.png' --exclude='*.tar.gz' \
                --exclude='old/' --exclude='*/old/' --exclude='.git/' \
                --exclude='venv/' --exclude='env/' --exclude='.venv/' \
                --exclude='site-packages/' --exclude='*/site-packages/' \
                --exclude='*/test_*.py' --exclude='test_*.py' \
                --exclude='*/tests/' --exclude='tests/' \
                . ${CLUSTER_USER}@${CLUSTER_HOST}:${REMOTE_DIR}/
            cd - > /dev/null
        else
            echo "rsync not found, using scp..."
            # Create temporary directory with proper structure
            TEMP_DIR=$(mktemp -d)
            echo "Creating filtered copy in ${TEMP_DIR}..."
            # Go up two levels and copy entire project
            cd ../..
            cp -r . ${TEMP_DIR}/project
            cd - > /dev/null
            # Remove excluded files (but keep .so files for test)
            find ${TEMP_DIR} -name "*.h5" -delete
            find ${TEMP_DIR} -name "*.png" -delete
            find ${TEMP_DIR} -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
            find ${TEMP_DIR} -name "*.pyc" -delete
            find ${TEMP_DIR} -name "*.tar.gz" -delete
            find ${TEMP_DIR} -name "old" -type d -exec rm -rf {} + 2>/dev/null || true
            find ${TEMP_DIR} -name ".git" -type d -exec rm -rf {} + 2>/dev/null || true
            find ${TEMP_DIR} -name "venv" -type d -exec rm -rf {} + 2>/dev/null || true
            find ${TEMP_DIR} -name "env" -type d -exec rm -rf {} + 2>/dev/null || true
            find ${TEMP_DIR} -name ".venv" -type d -exec rm -rf {} + 2>/dev/null || true
            find ${TEMP_DIR} -name "site-packages" -type d -exec rm -rf {} + 2>/dev/null || true
            find ${TEMP_DIR} -name "test_*.py" -delete
            find ${TEMP_DIR} -name "tests" -type d -exec rm -rf {} + 2>/dev/null || true
            # Transfer the entire project structure
            scp -r ${TEMP_DIR}/project/* ${CLUSTER_USER}@${CLUSTER_HOST}:${REMOTE_DIR}/
            # Clean up
            rm -rf ${TEMP_DIR}
        fi
        
        echo "Running system info check and setup verification..."
        ssh ${CLUSTER_USER}@${CLUSTER_HOST} \
            "cd ${REMOTE_DIR}/src/cluster && module load fast_python_workshop_cpu 2>/dev/null && echo '=== SYSTEM INFO ===' && gcc --version && python3 --version && uname -a && ulimit -s && echo '=== RUNNING SETUP ===' && python3 setup_cluster.py"
        ;;
    "from")
        echo "Downloading results from ETH HPC..."
        echo "Note: 'from' is deprecated. Use 'retrieve' for the primary download method."
        echo "=== RETRIEVING h5 FILES ==="
        ssh ${CLUSTER_USER}@${CLUSTER_HOST} \
            "cd ${REMOTE_DIR}/src/cluster 2>/dev/null && \
            tar -czf collected_results_$(date +%Y%m%d_%H%M%S).tar.gz bootstrap_data/*.h5 2>/dev/null"
        newest_file=$(ssh ${CLUSTER_USER}@${CLUSTER_HOST} "ls -t ${REMOTE_DIR}/src/cluster/collected_results_*.tar.gz 2>/dev/null | head -1")
        if [ -n "$newest_file" ]; then
            scp ${CLUSTER_USER}@${CLUSTER_HOST}:"$newest_file" ./
            echo "Downloaded newest collected_results_*.tar.gz file to local directory."
            tar -xzf collected_results_*.tar.gz
            echo "Extracted collected_results_*.tar.gz file."
        else
            echo "No tar files found. No results to download."
            exit 1
        fi
        ;;
    "status")
        echo "Checking job status..."
        ssh ${CLUSTER_USER}@${CLUSTER_HOST} "squeue -u ${CLUSTER_USER}"
        ;;
    "clean")
        echo "Removing unwanted files from cluster..."
        ssh ${CLUSTER_USER}@${CLUSTER_HOST} \
            "find ${REMOTE_DIR} -name '*.h5' -delete; find ${REMOTE_DIR} -name '*.png' -delete; find ${REMOTE_DIR} -name '__pycache__' -type d -exec rm -rf {} + 2>/dev/null || true"
        echo "Cleanup complete!"
        ;;
    "list")
        echo "Listing files on cluster..."
        ssh ${CLUSTER_USER}@${CLUSTER_HOST} \
            "if command -v tree >/dev/null 2>&1; then tree ${REMOTE_DIR}; else find ${REMOTE_DIR} -type f | sort; fi"
        ;;
    "delete")
        echo "WARNING: This will delete ALL files in ${REMOTE_DIR} on the cluster!"
        echo "Are you sure? (y/N)"
        read -r confirmation
        if [[ "$confirmation" =~ ^[Yy]$ ]]; then
            echo "Deleting all files on cluster..."
            ssh ${CLUSTER_USER}@${CLUSTER_HOST} \
                "rm -rf ${REMOTE_DIR}"
            echo "All files deleted from cluster!"
        else
            echo "Deletion cancelled."
        fi
        ;;
    "logs")
        echo "Showing recent job logs..."
        ssh ${CLUSTER_USER}@${CLUSTER_HOST} \
            "cd ${REMOTE_DIR}/src/cluster && ls -la echemes_*.out echemes_*.err 2>/dev/null || echo 'No log files found yet'"
        echo ""
        echo "To view a specific log file, use: ./transfer.sh viewlog JOBID"
        ;;
    "viewlog")
        if [ -z "$2" ]; then
            echo "Usage: $0 viewlog JOBID"
            echo "Example: $0 viewlog 12345"
            exit 1
        fi
        JOBID="$2"
        echo "=== OUTPUT LOG (echemes_${JOBID}.out) ==="
        ssh ${CLUSTER_USER}@${CLUSTER_HOST} \
            "cd ${REMOTE_DIR}/src/cluster && cat echemes_${JOBID}.out 2>/dev/null || echo 'Output log not found'"
        echo ""
        echo "=== ERROR LOG (echemes_${JOBID}.err) ==="
        ssh ${CLUSTER_USER}@${CLUSTER_HOST} \
            "cd ${REMOTE_DIR}/src/cluster && cat echemes_${JOBID}.err 2>/dev/null || echo 'Error log not found'"
        ;;
    "check")
        echo "=== JOB STATUS ==="
        ssh ${CLUSTER_USER}@${CLUSTER_HOST} "squeue -u ${CLUSTER_USER}"
        echo ""
        echo "=== RECENT LOG FILES ==="
        ssh ${CLUSTER_USER}@${CLUSTER_HOST} \
            "cd ${REMOTE_DIR}/src/cluster 2>/dev/null && ls -la echemes_*.out echemes_*.err 2>/dev/null || echo 'No log files found'"
        echo ""
        echo "=== BOOTSTRAP DATA FILES ==="
        ssh ${CLUSTER_USER}@${CLUSTER_HOST} \
            "cd ${REMOTE_DIR}/src/cluster 2>/dev/null && ls -la bootstrap_data/*.h5 2>/dev/null || echo 'No h5 files found yet'"
        ;;
    "retrieve")
        echo "=== PRIMARY DOWNLOAD METHOD: RETRIEVING RESULTS ==="
        echo "Checking for completed bootstrap analysis results..."
        
        # Check if bootstrap_data directory exists and has h5 files
        bootstrap_count=$(ssh ${CLUSTER_USER}@${CLUSTER_HOST} "cd ${REMOTE_DIR}/src/cluster 2>/dev/null && ls -1 bootstrap_data/*.h5 2>/dev/null | wc -l" || echo "0")
        echo "Found $bootstrap_count h5 files in bootstrap_data directory"
        
        if [ "$bootstrap_count" -eq "0" ]; then
            echo "No h5 files found. Analysis may not be complete or failed."
            echo "Use './transfer.sh check' to verify job status and logs."
            exit 1
        fi
        
        # Create timestamped archive of results
        timestamp=$(date +%Y%m%d_%H%M%S)
        archive_name="collected_results_${timestamp}.tar.gz"
        echo "Creating archive: $archive_name"
        
        ssh ${CLUSTER_USER}@${CLUSTER_HOST} \
            "cd ${REMOTE_DIR}/src/cluster && \
            tar -czf $archive_name bootstrap_data/*.h5 2>/dev/null && \
            echo 'Archive created successfully: $archive_name'"
        
        # Download the archive
        echo "Downloading archive to local directory..."
        if scp ${CLUSTER_USER}@${CLUSTER_HOST}:${REMOTE_DIR}/src/cluster/$archive_name ./; then
            echo "✓ Download successful: $archive_name"
        else
            echo "✗ Download failed"
            exit 1
        fi
        
        # Extract the archive
        echo "Extracting results..."
        if tar -xzf $archive_name; then
            echo "✓ Extraction successful"
            echo "Results are now available in the ./bootstrap_data/ directory"
            ls -la bootstrap_data/*.h5 2>/dev/null || echo "No h5 files found after extraction"
        else
            echo "✗ Extraction failed"
            exit 1
        fi
        
        echo ""
        echo "=== DOWNLOAD COMPLETE ==="
        echo "Archive: $archive_name"
        echo "Results: ./bootstrap_data/"
        echo "Use data extraction tools to analyze the results."
        ;;
    *)
        echo "Usage: $0 {to|retrieve|from|test|status|check|logs|viewlog|clean|list|delete}"
        echo "  to           - Transfer files and submit job"
        echo "  retrieve     - Download results (PRIMARY METHOD)"
        echo "  from         - Download results (deprecated, use retrieve)"
        echo "  test         - Transfer files and run setup verification"
        echo "  status       - Check job status"
        echo "  check        - Check job status, logs, and output files"
        echo "  logs         - List available log files"
        echo "  viewlog JOBID - View specific job log (output and error)"
        echo "  clean        - Remove unwanted files from cluster"
        echo "  list         - List all files on cluster"
        echo "  delete       - Delete ALL files from cluster (with confirmation)"
        exit 1
        ;;
esac