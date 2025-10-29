#ifndef BCC_PARACRYSTAL_H
#define BCC_PARACRYSTAL_H

/**
 * Compute the bcc_paracrystal form factor.
 * 
 * @param q Scattering vector magnitude (1/Angstrom)
 * @param F1 Output: Form factor amplitude
 * @param F2 Output: Form factor squared
 * @param ... Model-specific parameters
 */
void compute_bcc_paracrystal_form_factor(double q, double *F1, double *F2, ...);

#endif // BCC_PARACRYSTAL_H
