# Example: Adding a Sphere Form Factor Model

This is a template/example for adding a new form factor model to the project.

## Step 1: Create Directory Structure

```
src/form_factor/sphere/
├── __init__.py
├── wrapper.py
├── sphere.c
└── sphere.h
```

## Step 2: Implement C Code (sphere.c)

```c
// sphere.c - Example implementation
#include <math.h>
#include "sphere.h"

void compute_sphere_form_factor(double q, double radius, double sld, 
                                 double solvent_sld, double *F, double *F2) {
    // Example: Simple sphere form factor
    double V = (4.0/3.0) * M_PI * pow(radius, 3);
    double contrast = sld - solvent_sld;
    double qr = q * radius;
    
    double form;
    if (qr < 1e-6) {
        form = 1.0;
    } else {
        form = 3.0 * (sin(qr) - qr * cos(qr)) / pow(qr, 3);
    }
    
    *F = V * contrast * form;
    *F2 = (*F) * (*F);
}
```

## Step 3: Create Header File (sphere.h)

```c
// sphere.h
#ifndef SPHERE_H
#define SPHERE_H

void compute_sphere_form_factor(double q, double radius, double sld, 
                                 double solvent_sld, double *F, double *F2);

#endif
```

## Step 4: Create Python Wrapper (wrapper.py)

```python
# wrapper.py
import ctypes
import os
import sys

# Load the shared library
_lib_path = os.path.join(os.path.dirname(__file__), 
                         'sphere.so' if sys.platform != 'win32' else 'sphere.pyd')
_lib = ctypes.CDLL(_lib_path)

# Define function signature
_lib.compute_sphere_form_factor.argtypes = [
    ctypes.c_double,  # q
    ctypes.c_double,  # radius
    ctypes.c_double,  # sld
    ctypes.c_double,  # solvent_sld
    ctypes.POINTER(ctypes.c_double),  # F
    ctypes.POINTER(ctypes.c_double)   # F2
]
_lib.compute_sphere_form_factor.restype = None

def compute_form_factor(q, sld, solvent_sld, radius):
    """
    Compute the form factor for a sphere.
    
    Parameters
    ----------
    q : float
        The scattering vector magnitude.
    sld : float
        The scattering length density of the sphere.
    solvent_sld : float
        The scattering length density of the solvent.
    radius : float
        The radius of the sphere.
    
    Returns
    -------
    tuple of float
        The integrated computed form factor (F) and form factor squared (F²).
    """
    F = ctypes.c_double()
    F2 = ctypes.c_double()
    
    _lib.compute_sphere_form_factor(q, radius, sld, solvent_sld, 
                                     ctypes.byref(F), ctypes.byref(F2))
    
    return F.value, F2.value
```

## Step 5: Create __init__.py

```python
# __init__.py
"""Sphere form factor model for scattering analysis."""
```

## Step 6: Update setup.py

Add to the `run()` method in `BuildSharedLibraries` class:

```python
# Build sphere shared library
self.build_shared_lib(
    'sphere',
    [
        'src/form_factor/sphere/sphere.c'
    ],
    'src/form_factor/sphere'
)
```

Update `package_data`:

```python
package_data={
    'form_factor.core_shell_cylinder': ['*.so', '*.pyd', '*.dll'],
    'form_factor.sphere': ['*.so', '*.pyd', '*.dll'],  # Add this line
    'structure_factor.hayter_msa': ['*.so', '*.pyd', '*.dll'],
},
```

## Step 7: Update utils.py

Change the global variable to use your new model:

```python
FORM_FACTOR_MODEL = "sphere"  # Changed from "core_shell_cylinder"
```

## Step 8: Update form_factor() function in utils.py (if needed)

You may need to update the `form_factor()` function signature in `utils.py` to match your model's parameters:

```python
def form_factor(q, sld, solvent_sld, radius):
    """
    Compute the form factor for the sphere model.
    
    Parameters
    ----------
    q : float
        The scattering vector magnitude.
    sld : float
        The scattering length density of the sphere.
    solvent_sld : float
        The scattering length density of the solvent.
    radius : float
        The radius of the sphere.
    
    Returns
    -------
    tuple of float
        The integrated computed form factor (F) and form factor squared (F²).
    """
    return compute_form_factor(q, sld, solvent_sld, radius)
```

## Step 9: Build and Install

```bash
cd /workspace/core_shell_cylinder_project
python setup.py build_py
pip install -e .
```

## Step 10: Test

```python
from utils import form_factor

# Test your new sphere form factor
F, F2 = form_factor(q=0.1, sld=4.0, solvent_sld=6.0, radius=50.0)
print(f"F = {F}, F² = {F2}")
```

## Notes

- The function signature of `compute_form_factor()` can vary between models
- You may need to update the `form_factor()` and related functions in `utils.py` to match your model's parameters
- For a completely different parameter set, consider creating model-specific wrappers
- Make sure to handle edge cases (e.g., q → 0) in your C implementation
