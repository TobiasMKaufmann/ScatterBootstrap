#ifndef PRINGLE_H
#define PRINGLE_H

/**
 * Compute the pringle form factor.
 * 
 * @param q Scattering vector magnitude (1/Angstrom)
 * @param F1 Output: Form factor amplitude
 * @param F2 Output: Form factor squared
 * @param ... Model-specific parameters
 */
void compute_pringle_form_factor(double q, double *F1, double *F2, ...);

#endif // PRINGLE_H
