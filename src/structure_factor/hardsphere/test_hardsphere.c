#include "../../lib/sas_core.h"

#include <stdio.h>
#include <math.h>

// Define FLOAT_SIZE for double precision
#define FLOAT_SIZE 8

// SINCOS macro - computes sin and cos at the same time
#define SINCOS(x, s, c) do { s = sin(x); c = cos(x); } while(0)

// The hardsphere structure factor function
double Iq(double q, double radius_effective, double volfraction)
{
      double D,A,B,G,X,X2,X4,S,C,FF,HARDSPH;
      // these are c compiler instructions, can also put normal code inside the "if else" structure
      #if FLOAT_SIZE > 4
      // double precision
      // orig had 0.2, don't call the variable cutoff as PAK already has one called that!
      // Must use UPPERCASE name please.
      // 0.05 better, 0.1 OK
      #define CUTOFFHS 0.05
      #else
      // 0.1 bad, 0.2 OK, 0.3 good, 0.4 better, 0.8 no good
      #define CUTOFFHS 0.4
      #endif

      if(fabs(radius_effective) < 1.E-12) {
               HARDSPH=1.0;
               return(HARDSPH);
      }
      // removing use of pow(xxx,2) and rearranging the calcs
      // of A, B & G cut ~40% off execution time ( 0.5 to 0.3 msec)
      X = 1.0/( 1.0 -volfraction);
      D= X*X;
      A= (1.+2.*volfraction)*D;
      A *=A;
      X=fabs(q*radius_effective*2.0);

      if(X < 5.E-06) {
                 HARDSPH=1./A;
                 return(HARDSPH);
      }
      X2 =X*X;
      B = (1.0 +0.5*volfraction)*D;
      B *= B;
      B *= -6.*volfraction;
      G=0.5*volfraction*A;

      if(X < CUTOFFHS) {
      // RKH Feb 2016, use Taylor series expansion for small X
      // else no obvious way to rearrange the equations to avoid
      // needing a very high number of significant figures.
      // Series expansion found using Mathematica software. Numerical test
      // in .xls showed terms to X^2 are sufficient
      // for 5 or 6 significant figures, but I put the X^4 one in anyway
            //FF = 8*A +6*B + 4*G - (0.8*A +2.0*B/3.0 +0.5*G)*X2 +(A/35. +B/40. +G/50.)*X4;
            // refactoring the polynomial makes it very slightly faster (0.5 not 0.6 msec)
            //FF = 8*A +6*B + 4*G + ( -0.8*A -2.0*B/3.0 -0.5*G +(A/35. +B/40. +G/50.)*X2)*X2;

            FF = 8.0*A +6.0*B + 4.0*G + ( -0.8*A -B/1.5 -0.5*G +(A/35. +0.0125*B +0.02*G)*X2)*X2;

            // combining the terms makes things worse at smallest Q in single precision
            //FF = (8-0.8*X2)*A +(3.0-X2/3.)*2*B + (4+0.5*X2)*G +(A/35. +B/40. +G/50.)*X4;
            // note that G = -volfraction*A/2, combining this makes no further difference at smallest Q
            //FF = (8 +2.*volfraction + ( volfraction/4. -0.8 +(volfraction/100. -1./35.)*X2 )*X2 )*A  + (3.0 -X2/3. +X4/40.)*2.*B;
            HARDSPH= 1./(1. + volfraction*FF );
            return(HARDSPH);
      }
      X4=X2*X2;
      SINCOS(X,S,C);

// RKH Feb 2016, use version FISH code as is better than original sasview one
// at small Q in single precision, and more than twice as fast in double.
      //FF=A*(S-X*C)/X + B*(2.*X*S -(X2-2.)*C -2.)/X2 + G*( (4.*X2*X -24.*X)*S -(X4 -12.*X2 +24.)*C +24. )/X4;
      // refactoring the polynomial here & above makes it slightly faster

      FF=  (( G*( (4.*X2 -24.)*X*S -(X4 -12.*X2 +24.)*C +24. )/X2 + B*(2.*X*S -(X2-2.)*C -2.) )/X + A*(S-X*C))/X ;
      HARDSPH= 1./(1. + 24.*volfraction*FF/X2 );

      return(HARDSPH);
}

int main() {
    // Test parameters
    double q_values[] = {0.001, 0.01, 0.05, 0.1, 0.2, 0.3, 0.5};
    double radius_effective = 50.0;  // Angstroms
    double volfraction = 0.2;        // 20% volume fraction
    
    printf("Testing Hardsphere Structure Factor\n");
    printf("=====================================\n");
    printf("Parameters:\n");
    printf("  Effective radius: %.2f Angstroms\n", radius_effective);
    printf("  Volume fraction: %.3f\n\n", volfraction);
    printf("q (1/Angstrom)    S(q)\n");
    printf("-------------------------------\n");
    
    for(int i = 0; i < 7; i++) {
        double q = q_values[i];
        double S_q = Iq(q, radius_effective, volfraction);
        printf("  %.4f          %.6f\n", q, S_q);
    }
    
    printf("\n");
    
    // Test edge cases
    printf("Edge case tests:\n");
    printf("-------------------------------\n");
    
    // Very small radius (should return 1.0)
    double S_zero_radius = Iq(0.1, 1e-15, 0.2);
    printf("Zero radius (q=0.1): %.6f (expected ~1.0)\n", S_zero_radius);
    
    // Very small q
    double S_small_q = Iq(1e-7, 50.0, 0.2);
    printf("Very small q (1e-7): %.6f\n", S_small_q);
    
    // Zero volume fraction (no interaction, S(q) should be ~1.0)
    double S_zero_vf = Iq(0.1, 50.0, 0.0);
    printf("Zero volume fraction: %.6f (expected ~1.0)\n", S_zero_vf);
    
    return 0;
}
