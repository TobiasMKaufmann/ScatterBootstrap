#ifndef CORE_SHELL_CYLINDER_H
#define CORE_SHELL_CYLINDER_H

// Core-shell cylinder scattering form factors
void Fq(double q, double *F1, double *F2, double core_sld, double shell_sld, double solvent_sld, double radius, double thickness, double length);

// Core-shell cylinder scattering intensity for specific orientation
double Iqac(double qab, double qc, double core_sld, double shell_sld, double solvent_sld, double radius, double thickness, double length);

#endif // CORE_SHELL_CYLINDER_H
