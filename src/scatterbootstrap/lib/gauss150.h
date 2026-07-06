#ifndef GAUSS150_H
#define GAUSS150_H

/**
 * 150-point Gaussian quadrature weights and abscissas
 * for integration over [-1, 1]
 */

// On Windows, data symbols need explicit import/export decoration
#ifdef _WIN32
  #ifdef BUILDING_SAS_CORE
    #define SAS_DATA_EXPORT __declspec(dllexport)
  #else
    #define SAS_DATA_EXPORT __declspec(dllimport)
  #endif
#else
  #define SAS_DATA_EXPORT
#endif

#define GAUSS150_N 150

SAS_DATA_EXPORT extern const double GAUSS150_Z[GAUSS150_N];
SAS_DATA_EXPORT extern const double GAUSS150_W[GAUSS150_N];

#endif // GAUSS150_H
