#ifndef UTILS_H
#define UTILS_H

#include <math.h>

// Mathematical constants
#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

#ifndef M_4PI_3
#define M_4PI_3 (4.0 * M_PI / 3.0)
#endif

// Utility functions
void SINCOS(double x, double *s, double *c);
double sas_sinx_x(double x);

// Mathematical helper functions
static inline double square(double x) {
    return x * x;
}

static inline double cube(double x) {
    return x * x * x;
}

#endif // UTILS_H
