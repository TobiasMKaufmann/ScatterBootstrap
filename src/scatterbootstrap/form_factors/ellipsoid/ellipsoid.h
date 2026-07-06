#ifndef ELLIPSOID_H
#define ELLIPSOID_H

/**
 * Compute the ellipsoid form factor.
 * 
 * @param q Scattering vector magnitude (1/Angstrom)
 * @param F1 Output: Form factor amplitude
 * @param F2 Output: Form factor squared
 * @param ... Model-specific parameters
 */
void compute_ellipsoid_form_factor(double q, double *F1, double *F2, ...);

#endif // ELLIPSOID_H
