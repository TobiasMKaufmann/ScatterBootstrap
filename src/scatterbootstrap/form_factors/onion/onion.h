#ifndef ONION_H
#define ONION_H

/**
 * Compute the onion form factor.
 * 
 * @param q Scattering vector magnitude (1/Angstrom)
 * @param F1 Output: Form factor amplitude
 * @param F2 Output: Form factor squared
 * @param ... Model-specific parameters
 */
void compute_onion_form_factor(double q, double *F1, double *F2, ...);

#endif // ONION_H
