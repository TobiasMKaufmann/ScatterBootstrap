#ifndef SAS_CORE_H
#define SAS_CORE_H

/**
 * SAS Core Library - Master Header
 * 
 * Include this file to get access to all SAS mathematical functions,
 * constants, and utilities needed for form factor calculations.
 * 
 * Usage:
 *   #include "sas_core.h"
 * 
 * Or include individual headers as needed:
 *   #include "sas_math.h"
 *   #include "sas_constants.h"
 *   #include "utils.h"
 *   #include "gauss76.h"
 */

// Mathematical constants
#include "sas_constants.h"

// SAS special functions (Bessel, sinc, etc.)
#include "sas_math.h"

// Utility functions (square, cube, SINCOS, etc.)
#include "utils.h"

// Gaussian quadrature
#include "gauss76.h"

// Integer-order Bessel functions
#include "sas_JN.h"

// For models needing 150-point quadrature
// #include "gauss150.h"

// Polynomial evaluation (for special functions)
// #include "polevl.h"

#endif // SAS_CORE_H
