#ifndef SAS_JN_H
#define SAS_JN_H

/**
 * Bessel function of integer order Jn(x)
 * 
 * @param n Order (integer)
 * @param x Input value
 * @return Jn(x)
 */
double cephes_jn(int n, double x);
float cephes_jnf(int n, float x);

// Convenience macros
#if FLOAT_SIZE > 4
#define sas_JN cephes_jn
#else
#define sas_JN cephes_jnf
#endif

#endif // SAS_JN_H
