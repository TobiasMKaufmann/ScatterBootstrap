#ifndef UTILS_H
#define UTILS_H

#include <math.h>
#include "sas_constants.h"

// Utility functions
void SINCOS(double x, double *s, double *c);
double sas_sinx_x(double x);

// Mathematical helper functions (inline for performance)
static inline double square(double x) {
    return x * x;
}

static inline double cube(double x) {
    return x * x * x;
}

// cbrt and expm1 are part of C99/POSIX math.h
// On Windows/MSVC they might not be available, so provide fallback
#ifdef _MSC_VER
#ifndef cbrt
static inline double cbrt(double x) {
    return pow(x, 1.0/3.0);
}
#endif

#ifndef expm1
static inline double expm1(double x) {
    // expm1(x) = exp(x) - 1, accurate for small x
    if (fabs(x) < 1e-5) {
        return x + 0.5*x*x;
    }
    return exp(x) - 1.0;
}
#endif
#endif // _MSC_VER

#endif // UTILS_H
