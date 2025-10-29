#ifndef HARDSPHERE_H
#define HARDSPHERE_H

/**
 * Compute the hardsphere structure factor using Percus-Yevick closure.
 * 
 * @param q Scattering vector magnitude (1/Angstrom)
 * @param radius_effective Effective hard sphere radius (Angstrom)
 * @param volfraction Volume fraction of hard spheres (0 to 1)
 * @return Structure factor S(q)
 */
double compute_hardsphere_structure_factor(double q, double radius_effective, double volfraction);

#endif // HARDSPHERE_H
