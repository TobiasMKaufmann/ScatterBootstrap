#include <math.h>
#include "utils.h"

void SINCOS(double x, double *s, double *c) {
    *s = sin(x);
    *c = cos(x);
}

double sas_sinx_x(double x) {
    return (x != 0.0) ? sin(x) / x : 1.0;
}
