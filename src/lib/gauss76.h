#ifndef GAUSS76_H
#define GAUSS76_H

extern const double Gauss76Wt[76];
extern const double Gauss76Z[76];

// Convenience macros for Gauss-Legendre quadrature
#define GAUSS_N 76
#define GAUSS_Z Gauss76Z
#define GAUSS_W Gauss76Wt

#endif // GAUSS76_H
