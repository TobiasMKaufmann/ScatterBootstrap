#ifndef SAS_J1_H
#define SAS_J1_H

/**
 * Bessel function of order one J1(x)
 * 
 * @param x Input value
 * @return J1(x)
 */
double cephes_j1(double x);
float cephes_j1f(float x);

/**
 * Bessel function 2*J1(x)/x
 * Used for cylinder form factors
 * 
 * @param x Input value
 * @return 2*J1(x)/x
 */
double sas_2J1x_x(double x);

#endif // SAS_J1_H
