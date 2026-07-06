#ifndef POLYMER_MICELLE_H
#define POLYMER_MICELLE_H

/**
 * Compute the polymer_micelle form factor.
 * 
 * @param q Scattering vector magnitude (1/Angstrom)
 * @param F1 Output: Form factor amplitude
 * @param F2 Output: Form factor squared
 * @param ... Model-specific parameters
 */
void compute_polymer_micelle_form_factor(double q, double *F1, double *F2, ...);

#endif // POLYMER_MICELLE_H
