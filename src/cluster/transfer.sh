#!/bin/bash
# ETH HPC transfer script

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
            # Transfer the entire project structure
            scp -r ${TEMP_DIR}/project/* ${CLUSTER_USER}@${CLUSTER_HOST}:${REMOTE_DIR}/
            # Clean up
            rm -rf ${TEMP_DIR}
        fi
        
        echo "Running C extension test..."
        ssh ${CLUSTER_USER}@${CLUSTER_HOST} \
            "cd ${REMOTE_DIR}/src/cluster && module load fast_python_workshop_cpu && echo '=== SYSTEM INFO ===' && gcc --version && python3 --version && uname -a && ulimit -s && echo '=== RUNNING TEST ===' && python3 test_c_extensions.py"
        ;;
    "from")
        echo "Transferring results from ETH HPC..."
        # Try rsync first, fall back to scp if rsync not available
        if command -v rsync >/dev/null 2>&1; then
            rsync -avz ${CLUSTER_USER}@${CLUSTER_HOST}:${REMOTE_DIR}/src/cluster/bootstrap_data/ \
                ./bootstrap_data/
        else
            echo "rsync not found, using scp..."
            scp -r ${CLUSTER_USER}@${CLUSTER_HOST}:${REMOTE_DIR}/src/cluster/bootstrap_data/ \
                ./bootstrap_data/
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
        echo "=== RETRIEVE h5 FILES ==="
        ssh ${CLUSTER_USER}@${CLUSTER_HOST} \
            "cd ${REMOTE_DIR}/src/cluster 2>/dev/null && \
            tar -czf collected_results_$(date +%Y%m%d_%H%M%S).tar.gz bootstrap_data/*.h5 2>/dev/null"
        newest_file=$(ssh ${CLUSTER_USER}@${CLUSTER_HOST} "ls -t ${REMOTE_DIR}/src/cluster/collected_results_*.tar.gz 2>/dev/null | head -1")
        if [ -n "$newest_file" ]; then
            scp ${CLUSTER_USER}@${CLUSTER_HOST}:"$newest_file" ./
        else
            echo ""
            echo "No tar files found"
            exit
        fi
        echo ""
        echo "Downloaded newest collected_results_*.tar.gz files to local directory."
        tar -xzf collected_results_*.tar.gz
        echo ""
        echo "Extracted collected_results_*.tar.gz files."
    ;;
    *)
        echo "Usage: $0 {to|from|test|status|clean|list|delete|check|logs|viewlog}"
        echo "  to           - Transfer files and submit job"
        echo "  from         - Download results"
        echo "  test         - Transfer files and run C extension test only"
        echo "  status       - Check job status"
        echo "  clean        - Remove unwanted files from cluster"
        echo "  list         - List all files on cluster"
        echo "  delete       - Delete ALL files from cluster (with confirmation)"
        echo "  check        - Check job status, logs, and output files"
        echo "  logs         - List available log files"
        echo "  viewlog JOBID - View specific job log (output and error)"
        exit 1
        ;;
esac