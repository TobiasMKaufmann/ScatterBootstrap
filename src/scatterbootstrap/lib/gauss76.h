#ifndef GAUSS76_H
#define GAUSS76_H

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

SAS_DATA_EXPORT extern const double Gauss76Wt[76];
SAS_DATA_EXPORT extern const double Gauss76Z[76];

// Convenience macros for Gauss-Legendre quadrature
#define GAUSS_N 76
#define GAUSS_Z Gauss76Z
#define GAUSS_W Gauss76Wt

#endif // GAUSS76_H
