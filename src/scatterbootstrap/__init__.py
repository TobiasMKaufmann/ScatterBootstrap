"""
ScatterBootstrap: Small-angle scattering form factor and structure factor
models with bootstrap-based uncertainty quantification.
"""

from .core import (
    form_factor,
    structure_factor,
    intensity,
    fit_data,
    residuals_bootstrap,
    fit_bootstrap_many,
    compute_confidence_intervals,
    plot_data,
    plot_fit_data,
    list_form_factor_models,
    list_structure_factor_models,
)

__version__ = "0.4.0"

__all__ = [
    "form_factor",
    "structure_factor",
    "intensity",
    "fit_data",
    "residuals_bootstrap",
    "fit_bootstrap_many",
    "compute_confidence_intervals",
    "plot_data",
    "plot_fit_data",
    "list_form_factor_models",
    "list_structure_factor_models",
    "__version__",
]
