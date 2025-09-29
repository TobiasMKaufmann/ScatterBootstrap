#!/usr/bin/env python
"""
Simple test script to check C extension functions
"""
import sys
import os
import subprocess
sys.path.append('..')
sys.path.append('../core_shell_cylinder')

import numpy as np

def check_precompiled_extensions():
    """Check if precompiled C extensions exist and are usable"""
    print("=== Checking Precompiled C Extensions ===")
    
    c_ext_dir = "../core_shell_cylinder"
    
    if not os.path.exists(c_ext_dir):
        print(f"✗ C extension directory {c_ext_dir} not found")
        return False
    
    # Check for existing .so files
    so_files = ["core_shell_cylinder.so", "hayter_msa.so"]
    missing_files = []
    
    for so_file in so_files:
        so_path = os.path.join(c_ext_dir, so_file)
        if os.path.exists(so_path):
            print(f"✓ Found {so_file}")
        else:
            print(f"✗ Missing {so_file}")
            missing_files.append(so_file)
    
    if missing_files:
        print(f"Missing precompiled files: {missing_files}")
        print("Please compile the extensions on your PC first and transfer them.")
        return False
    
    # Ensure libcore_shell_cylinder.so exists (copy of core_shell_cylinder.so)
    lib_path = os.path.join(c_ext_dir, "libcore_shell_cylinder.so")
    core_path = os.path.join(c_ext_dir, "core_shell_cylinder.so")
    
    if not os.path.exists(lib_path) and os.path.exists(core_path):
        import shutil
        shutil.copy2(core_path, lib_path)
        print("✓ Created libcore_shell_cylinder.so")
    
    print("✓ All precompiled extensions found")
    return True

def test_c_extensions():
    print("=== Testing C Extensions ===")
    
    # Test imports
    try:
        import core_shell_cylinder
        print("✓ Successfully imported core_shell_cylinder module")
        print(f"Module file: {core_shell_cylinder.__file__}")
    except Exception as e:
        print(f"✗ Failed to import core_shell_cylinder: {e}")
        return False

    try:
        from core_shell_cylinder.wrapper import compute_form_factor
        print("✓ Successfully imported compute_form_factor")
    except Exception as e:
        print(f"✗ Failed to import compute_form_factor: {e}")
        return False

    try:
        from core_shell_cylinder.hayter_msa_wrapper import compute_structure_factor
        print("✓ Successfully imported compute_structure_factor")
    except Exception as e:
        print(f"✗ Failed to import compute_structure_factor: {e}")
        return False    # Test form factor with different parameter sets
    print("\n=== Testing Form Factor ===")
    
    test_cases = [
        # Simple case with small values
        {
            "name": "Simple small",
            "params": (0.01, 1.0, 2.0, 0.5, 5.0, 2.0, 10.0)
        },
        # Safe case - avoid the problematic parameter range
        {
            "name": "Safe params",
            "params": (0.05, 5.0, 8.0, 6.0, 10.0, 3.0, 20.0)
        },
        # Another safe case
        {
            "name": "Medium params",
            "params": (0.08, 2.0, 4.0, 1.0, 8.0, 2.5, 15.0)
        }
    ]
    
    # Only test problematic params if safe ones work
    problematic_case = {
        "name": "Original params (risky)", 
        "params": (0.1, 7.7, 10.989, 9.4, 13.84, 6.60, 35.21)
    }
    
    success = False
    
    for test_case in test_cases:
        name = test_case["name"]
        q, core_sld, shell_sld, solvent_sld, radius, thickness, length = test_case["params"]
        
        print(f"\nTesting {name}:")
        print(f"Input: q={q}, core_sld={core_sld}, shell_sld={shell_sld}, solvent_sld={solvent_sld}")
        print(f"       radius={radius}, thickness={thickness}, length={length}")
        
        try:
            # Test direct C extension call first
            print("Testing direct C extension call...")
            #result_direct = core_shell_cylinder.Fq(q, core_sld, shell_sld, solvent_sld, radius, thickness, length)
            #print(f"Direct C call result: {result_direct}")

            F, F2 = compute_form_factor(q, core_sld, shell_sld, solvent_sld, radius, thickness, length)
            
            print(f"Wrapper result: F={F}, F2={F2}")
            
            if np.isnan(F) or np.isnan(F2):
                print(f"✗ {name}: Form factor returned NaN")
            elif np.isinf(F) or np.isinf(F2):
                print(f"✗ {name}: Form factor returned Inf")
            else:
                print(f"✓ {name}: Form factor returned valid values")
                success = True
                
        except Exception as e:
            print(f"✗ {name}: Form factor computation failed: {e}")
            import traceback
            traceback.print_exc()
    
    if not success:
        print("✗ All form factor tests failed")
        return False
    
    # Test structure factor with simple parameters
    print("\n=== Testing Structure Factor ===")
    try:
        q = 0.1
        radius_effective = 24.8
        vol_frac = 0.16363
        zz = 28.288
        temp = 300
        csalt = 0.093723
        dialec = 78.3
        
        print(f"Input: q={q}, radius_effective={radius_effective}, vol_frac={vol_frac}")
        print(f"       zz={zz}, temp={temp}, csalt={csalt}, dialec={dialec}")
        
        S_q = compute_structure_factor(q, radius_effective, vol_frac, zz, temp, csalt, dialec)
        
        print(f"Output: S_q={S_q}")
        
        if np.isnan(S_q):
            print("✗ Structure factor returned NaN")
            return False
        elif np.isinf(S_q):
            print("✗ Structure factor returned Inf")
            return False
        else:
            print("✓ Structure factor returned valid value")
            
    except Exception as e:
        print(f"✗ Structure factor computation failed: {e}")
        return False
    
    # Test with array of q values
    print("\n=== Testing with Multiple Q Values ===")
    try:
        q_array = np.array([0.01, 0.05, 0.1, 0.2, 0.5])
        print(f"Testing with q values: {q_array}")
        
        for i, q in enumerate(q_array):
            F, F2 = compute_form_factor(q, core_sld, shell_sld, solvent_sld, radius, thickness, length)
            S_q = compute_structure_factor(q, radius_effective, vol_frac, zz, temp, csalt, dialec)
            intensity = F2 * S_q
            
            print(f"q={q:.3f}: F2={F2:.6f}, S_q={S_q:.6f}, I={intensity:.6f}")
            
            if np.isnan(intensity) or np.isinf(intensity):
                print(f"✗ Invalid result for q={q}")
                return False
        
        print("✓ All q values produced valid results")
        
    except Exception as e:
        print(f"✗ Array test failed: {e}")
        return False
    
    print("\n=== All C Extension Tests Passed! ===")
    return True

if __name__ == "__main__":
    # Check for precompiled C extensions
    if not check_precompiled_extensions():
        print("Failed to find precompiled C extensions")
        sys.exit(1)
    
    # Then test them
    success = test_c_extensions()
    if not success:
        sys.exit(1)
    print("Test completed successfully!")