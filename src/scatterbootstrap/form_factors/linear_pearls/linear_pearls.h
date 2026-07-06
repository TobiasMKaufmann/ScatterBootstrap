#ifndef LINEAR_PEARLS_H
#define LINEAR_PEARLS_H

/**
 * Compute the linear_pearls form factor.
 * 
 * @param q Scattering vector magnitude (1/Angstrom)
 * @param F1 Output: Form factor amplitude
 * @param F2 Output: Form factor squared
 * @param ... Model-specific parameters
 */
void compute_linear_pearls_form_factor(double q, double *F1, double *F2, ...);

#endif // LINEAR_PEARLS_H
