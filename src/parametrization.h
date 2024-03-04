#ifndef PARAMETRIZATION_H
#define PARAMETRIZATION_H

#include <stdint.h>


#ifdef F419

#define LIMBS 1
#define NUM_PRIMES 3
#define MAX_EXPONENT 10

#else

#define LIMBS 8
#define NUM_PRIMES 74
#define MAX_EXPONENT 5 /* (2*5+1)^74 is roughly 2^256 */

#endif

typedef struct uint_c { uint64_t c[LIMBS]; } uint_c;
typedef struct fp { uint64_t c[LIMBS]; } fp;
typedef struct proj { struct fp x, z; } proj;


extern const unsigned primes[NUM_PRIMES];

extern const uint64_t pbits;

extern const uint_c p;
extern const uint_c p_plus_one;
extern const uint_c p_minus_2;
extern const uint_c p_minus_1_halves;
extern const uint_c four_sqrt_p;

extern const fp fp_0;
extern const fp fp_1;
extern const fp r_squared_mod_p;

extern const uint64_t inv_min_p_mod_r;


#endif