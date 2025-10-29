#ifndef FCC_PARACRYSTAL_H
#define FCC_PARACRYSTAL_H

/**
 * Compute the fcc_paracrystal form factor.
 * 
 * @param q Scattering vector magnitude (1/Angstrom)
 * @param F1 Output: Form factor amplitude
 * @param F2 Output: Form factor squared
 * @param ... Model-specific parameters
 */
void compute_fcc_paracrystal_form_factor(double q, double *F1, double *F2, ...);

#endif // FCC_PARACRYSTAL_H
