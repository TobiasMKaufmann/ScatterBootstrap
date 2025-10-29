#ifndef CORE_MULTI_SHELL_H
#define CORE_MULTI_SHELL_H

/**
 * Compute the core_multi_shell form factor.
 * 
 * @param q Scattering vector magnitude (1/Angstrom)
 * @param F1 Output: Form factor amplitude
 * @param F2 Output: Form factor squared
 * @param ... Model-specific parameters
 */
void compute_core_multi_shell_form_factor(double q, double *F1, double *F2, ...);

#endif // CORE_MULTI_SHELL_H
