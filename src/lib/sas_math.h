#ifndef SAS_MATH_H
#define SAS_MATH_H

/**
 * SAS Mathematical Functions
 * 
 * This header provides special functions commonly used in small-angle scattering
 * calculations, including Bessel functions and their derivatives.
 */

// Bessel function j1(x)/x = (2*J1(x)/x - 1)
// Used for spherical form factors
double sas_J1(double x);

// 2*J1(x)/x, used in many form factor calculations
double sas_2J1x_x(double x);

// 3*j1(x)/x = 3*(sin(x)-x*cos(x))/x^3
// Used for spherical form factors: <f^2> = [3*j1(qR)/(qR)]^2
double sas_3j1x_x(double x);

// J0(x) - Bessel function of first kind, order 0
double sas_J0(double x);

// JN(n, x) - Bessel function of first kind, order n
double sas_JN(int n, double x);

// sinc(x) = sin(x)/x
double sas_sinx_x(double x);

// Gamma function
double sas_gamma(double x);

#endif // SAS_MATH_H
