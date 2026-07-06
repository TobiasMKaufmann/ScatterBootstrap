# Example: Adding a New Form Factor Model

This is a complete, worked example for adding a new scattering model to
ScatterBootstrap. It uses the bundled **sphere** model as the template. The same
recipe applies to structure factors (use `structure_factors/` and expose `Iq`).

The framework **auto-discovers and auto-compiles** models: once the files below
exist, `pip install -e .` builds the C extension and the model becomes available
by name through `scatterbootstrap.form_factor("<name>", ...)`. You do **not** edit
`setup.py` or `core.py`.

## Step 1: Create the directory structure

```
src/scatterbootstrap/form_factors/sphere/
├── __init__.py
├── wrapper.py
├── sphere.c
└── sphere.h
```

## Step 2: Implement the C kernel (`sphere.c`)

Form factor kernels expose a non-`static` `Fq(...)` function that writes the
orientationally-averaged amplitude `<F>` into `*f1` and the intensity `<F^2>`
into `*f2`. Reuse the shared numerical core (Bessel functions, quadrature,
constants) via `sas_core.h`.

```c
/* sphere.c -- adapted from SasView (https://www.sasview.org/), BSD-3-Clause */
#include "../../lib/sas_core.h"

void Fq(double q,
        double *f1,
        double *f2,
        double sld,
        double sld_solvent,
        double radius)
{
    const double bes = sas_3j1x_x(q * radius);          /* 3 j1(qr) / (qr) */
    const double contrast = sld - sld_solvent;
    const double volume = M_4PI_3 * radius * radius * radius;
    const double fq = contrast * volume * bes;
    *f1 = 1.0e-2 * fq;          /* scale to convenient units */
    *f2 = 1.0e-4 * fq * fq;
}
```

## Step 3: Create the header (`sphere.h`)

```c
#ifndef SPHERE_H
#define SPHERE_H

void Fq(double q, double *f1, double *f2,
        double sld, double sld_solvent, double radius);

#endif
```

## Step 4: Create the Python wrapper (`wrapper.py`)

The wrapper must expose `compute_form_factor(q, **params)` returning an array of
`F^2` values. Use `find_library` to locate the compiled binary across platforms.

```python
"""Python wrapper for the sphere form factor C extension."""
import ctypes
import os

import numpy as np

from ..._lib_finder import find_library

_lib = ctypes.CDLL(find_library("sphere", os.path.dirname(__file__)))
_lib.Fq.restype = None
_lib.Fq.argtypes = [
    ctypes.c_double,                  # q
    ctypes.POINTER(ctypes.c_double),  # f1 (out)
    ctypes.POINTER(ctypes.c_double),  # f2 (out)
    ctypes.c_double,                  # sld
    ctypes.c_double,                  # sld_solvent
    ctypes.c_double,                  # radius
]


def compute_form_factor(q, sld, sld_solvent, radius, **kwargs):
    """Compute |F(q)|^2 for a homogeneous sphere.

    Parameters
    ----------
    q : array_like
        Scattering vector magnitude(s) in inverse Angstroms.
    sld, sld_solvent : float
        Scattering length densities of the sphere and solvent.
    radius : float
        Sphere radius in Angstroms.
    **kwargs : dict
        Extra parameters are ignored (lets callers pass a shared param dict).
    """
    q = np.atleast_1d(q).astype(float)
    out = np.zeros_like(q)
    f1, f2 = ctypes.c_double(), ctypes.c_double()
    for i, q_val in enumerate(q):
        _lib.Fq(q_val, ctypes.byref(f1), ctypes.byref(f2), sld, sld_solvent, radius)
        out[i] = f2.value
    return out
```

> **Tip:** accepting `**kwargs` lets the fitting layer pass one combined parameter
> dictionary (form factor + structure factor params) to every model.

## Step 5: Create `__init__.py`

```python
"""Sphere form factor model."""
from .wrapper import compute_form_factor

__all__ = ["compute_form_factor"]
```

## Step 6: Build

```bash
pip install -e .          # compiles libsas_core + every model, including yours
```

The build system discovers any directory under `form_factors/` (or
`structure_factors/`) that contains a `<name>.c` file. No edits to `setup.py`.

## Step 7: Use it

```python
import scatterbootstrap as sb

print(sb.list_form_factor_models())     # "sphere" now appears
F2 = sb.form_factor(0.1, "sphere", sld=4e-6, sld_solvent=1e-6, radius=50)
I = sb.intensity(0.1, scale=1.0, background=0.001,
                 form_factor_model="sphere",
                 sld=4e-6, sld_solvent=1e-6, radius=50)
```

## Step 8: Add a test

Add a representative parameter set to `tests/conftest.py` so the parametrized
smoke tests cover your model, then run the suite:

```bash
pytest
```

## Notes

- Export functions must **not** be `static`; on Windows the build system detects
  and exports `Fq`/`Iq` automatically.
- Structure factors expose `Iq(q, ...)` and a `compute_structure_factor(q, ...)`
  wrapper instead.
- List-valued parameters (e.g. per-shell SLDs) are supported transparently by the
  fitting layer — see the `onion` and `core_multi_shell` models.
- Always handle the `q -> 0` limit in the C kernel to avoid division by zero.
