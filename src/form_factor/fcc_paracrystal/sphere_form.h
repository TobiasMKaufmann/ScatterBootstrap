#ifndef SPHERE_FORM_H
#define SPHERE_FORM_H

/**
 * Sphere form factor functions for paracrystal models.
 * 
 * These functions compute the form factor for spherical particles,
 * used by BCC and FCC paracrystal structure factors.
 */

/**
 * Calculate the volume of a sphere.
 * 
 * @param radius Sphere radius in Angstroms
 * @return Volume in cubic Angstroms
 */
double sphere_volume(double radius);

/**
 * Calculate the form factor for a sphere.
 * 
 * @param q Scattering vector magnitude (1/Angstrom)
 * @param radius Sphere radius in Angstroms
 * @param sld Scattering length density of the sphere (1/Angstrom^2)
 * @param solvent_sld Scattering length density of the solvent (1/Angstrom^2)
 * @return Form factor intensity
 */
double sphere_form(double q, double radius, double sld, double solvent_sld);

#endif // SPHERE_FORM_H
