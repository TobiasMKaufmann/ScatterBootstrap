#!/usr/bin/env python3
"""
Simple script to collect h5 files from cluster processing.
"""
import os
import shutil
from pathlib import Path

def main():
    """Collect all h5 files from bootstrap_data directory"""
    source_dir = Path("bootstrap_data")
    dest_dir = Path("collected_results")
    
    print(f"Collecting h5 files from {source_dir}")
    
    if not source_dir.exists():
        print("No bootstrap_data directory found")
        return
    
    # Create destination
    dest_dir.mkdir(exist_ok=True)
    
    # Copy all h5 files
    h5_files = list(source_dir.glob("*.h5"))
    
    if not h5_files:
        print("No h5 files found")
        return
    
    print(f"Found {len(h5_files)} files:")
    for h5_file in h5_files:
        dest_file = dest_dir / h5_file.name
        shutil.copy2(h5_file, dest_file)
        size_mb = h5_file.stat().st_size / 1024 / 1024
        print(f"  {h5_file.name} ({size_mb:.1f} MB)")
    
    print(f"\nAll files copied to {dest_dir}")

if __name__ == "__main__":
    main()
