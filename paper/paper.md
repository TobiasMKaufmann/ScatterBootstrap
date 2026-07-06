---
title: 'ScatterBootstrap: Small-angle scattering model fitting with bootstrap-based uncertainty quantification'
tags:
  - Python
  - small-angle scattering
  - SAXS
  - SANS
  - form factor
  - structure factor
  - bootstrap
  - uncertainty quantification
authors:
  - name: Tobias Kaufmann
    orcid: 0000-0000-0000-0000  # TODO: replace with the author's real ORCID
    affiliation: 1
affiliations:
  - name: ETH Zürich, Switzerland
    index: 1
date: 12 June 2026
bibliography: paper.bib
---

# Summary

Small-angle X-ray and neutron scattering (SAXS/SANS) are widely used to probe
the size, shape, and interactions of nanoscale objects in solution. Quantitative
interpretation is usually done by fitting a physical model — a *form factor*
describing single-particle scattering, optionally multiplied by a *structure
factor* describing interparticle correlations — to the measured intensity curve
$I(q)$ [@pedersen1997analysis]. While many tools can perform such fits, robustly
estimating the *uncertainty* of the recovered parameters remains awkward,
particularly when measurement errors are non-Gaussian, correlated, or simply not
reported.

`ScatterBootstrap` is a Python package that combines a library of compiled,
high-performance scattering models with a residual-bootstrap workflow for
uncertainty quantification. It bundles 14 form factor models and 2 structure
factor models, each implemented as a small C extension and exposed through a
uniform, name-based Python API. The same models that are used to fit a dataset
are reused to resample fit residuals [@efron1979bootstrap; @efron1994introduction],
refit thousands of synthetic datasets, and report percentile confidence intervals
for every fitted parameter. A batch-processing layer (including optional SLURM/HPC
helpers) makes it practical to apply this analysis to large collections of curves.

# Statement of need

Researchers fitting SAXS/SANS data routinely need parameter uncertainties, not
just point estimates. The covariance matrix returned by a least-squares fit
relies on assumptions (correct, independent, Gaussian errors and a locally linear
model) that are frequently violated for scattering data, and many experimental
datasets do not ship per-point error bars at all. Bootstrapping the fit residuals
sidesteps these assumptions and produces empirical confidence intervals directly
from the data and the model.

General-purpose SAS packages such as SasView [@sasview] provide extensive model
libraries and interactive fitting, but a scriptable, dependency-light pipeline
that pairs those models with a reproducible bootstrap uncertainty analysis — and
that scales to thousands of curves on a cluster — is not readily available.
`ScatterBootstrap` targets exactly this gap. Its design goals are:

- **Speed**: each model kernel is compiled C, sharing a common numerical core
  (Bessel functions, Gauss–Legendre quadrature, polynomial evaluation) adapted
  from the open-source SasView/sasmodels project [@sasview], giving one to two
  orders of magnitude speedup over equivalent pure-Python implementations and
  making large bootstrap ensembles tractable.
- **Reproducibility**: fits and bootstrap resampling are driven entirely from
  Python with explicit, seedable random number generators, so an analysis can be
  re-run deterministically.
- **Generality**: models are selected *by name* at call time rather than by
  editing source code, list-valued parameters (e.g. multi-shell scattering-length
  densities) are supported transparently, and new C models are discovered and
  compiled automatically by the build system.
- **Scale**: a batch layer stores inputs, fits, and full bootstrap ensembles in
  HDF5 and integrates with HPC schedulers for high-throughput studies.

The numerical building blocks rest on the scientific Python stack — NumPy
[@harris2020array], SciPy [@virtanen2020scipy] for non-linear least squares, and
Matplotlib [@hunter2007matplotlib] for visualization. The structure factor models
implement the analytic mean-spherical-approximation results of Hayter and Penfold
for charged macroions [@hayter1981analytic; @hansen1982rescaled] and the
hard-sphere reference system.

# Functionality

The public API is intentionally small. Scattering is evaluated with
`form_factor(q, model, **params)`, `structure_factor(q, model, **params)`, and
`intensity(q, scale, background, form_factor_model, structure_factor_model,
**params)`. Data analysis is performed with `fit_data` (a thin, bounds-aware
wrapper around `scipy.optimize.curve_fit`), `residuals_bootstrap` (residual
resampling and refitting with an optional HDF5 store), and
`compute_confidence_intervals` (percentile intervals from a bootstrap ensemble).
`list_form_factor_models()` and `list_structure_factor_models()` enumerate the
available models. Helper routines produce publication-quality plots of data and
fits.

Adding a new model requires only dropping a `<name>.c` kernel and a thin
`wrapper.py` into the appropriate package directory; the build system compiles it
and the discovery layer exposes it by name, with no edits to the core library.

# Acknowledgements

The scattering model kernels and shared numerical core are adapted from the
open-source SasView/sasmodels project [@sasview], whose contributors are
gratefully acknowledged.

# References
