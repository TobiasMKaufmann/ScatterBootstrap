#ifndef LAMELLAR_HG_H
#define LAMELLAR_HG_H

/**
 * Compute the lamellar_hg form factor.
 * 
 * @param q Scattering vector magnitude (1/Angstrom)
 * @param F1 Output: Form factor amplitude
 * @param F2 Output: Form factor squared
 * @param ... Model-specific parameters
 */
void compute_lamellar_hg_form_factor(double q, double *F1, double *F2, ...);

#endif // LAMELLAR_HG_H
