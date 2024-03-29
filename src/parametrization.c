#include "parametrization.h"

#ifdef F419

const unsigned primes[NUM_PRIMES] = {
    3, 5, 7};

const uint64_t pbits = 9;

const uint_c p = {{419}};

const uint_c p_plus_one = {{419 + 1}};

const fp fp_0 = {{0}};

/* 2^64 mod p*/
const fp fp_1 = {{0x199}};

/* (2^64)^2 mod  p */
const fp r_squared_mod_p = {{0x64}};

/* -p^-1 mod 2**64 */
const uint64_t inv_min_p_mod_r = 0xe656c24a8a14c5f5;

/* p - 2 */
const uint_c p_minus_2 = {{419 - 2}};

/* (p - 1) / 2 */
const uint_c p_minus_1_halves = {{(419 - 1) / 2}};

/* floor(4 sqrt(p)) */
const uint_c four_sqrt_p = {{0x51}};

#else

const unsigned primes[NUM_PRIMES] = {
    3,
    5,
    7,
    11,
    13,
    17,
    19,
    23,
    29,
    31,
    37,
    41,
    43,
    47,
    53,
    59,
    61,
    67,
    71,
    73,
    79,
    83,
    89,
    97,
    101,
    103,
    107,
    109,
    113,
    127,
    131,
    137,
    139,
    149,
    151,
    157,
    163,
    167,
    173,
    179,
    181,
    191,
    193,
    197,
    199,
    211,
    223,
    227,
    229,
    233,
    239,
    241,
    251,
    257,
    263,
    269,
    271,
    277,
    281,
    283,
    293,
    307,
    311,
    313,
    317,
    331,
    337,
    347,
    349,
    353,
    359,
    367,
    373,
    587,
};

const uint64_t pbits = 511;

const uint_c p = {{
    0x1b81b90533c6c87b,
    0xc2721bf457aca835,
    0x516730cc1f0b4f25,
    0xa7aac6c567f35507,
    0x5afbfcc69322c9cd,
    0xb42d083aedc88c42,
    0xfc8ab0d15e3e4c4a,
    0x65b48e8f740f89bf,
}};

const uint_c p_plus_one = {{0x1b81b90533c6c87c, 0xc2721bf457aca835, 0x516730cc1f0b4f25, 0xa7aac6c567f35507,
                            0x5afbfcc69322c9cd, 0xb42d083aedc88c42, 0xfc8ab0d15e3e4c4a, 0x65b48e8f740f89bf}};

const fp fp_0 = {{0}};

/* 2^512 mod p */
const fp fp_1 = {{
    0xc8fc8df598726f0a,
    0x7b1bc81750a6af95,
    0x5d319e67c1e961b4,
    0xb0aa7275301955f1,
    0x4a080672d9ba6c64,
    0x97a5ef8a246ee77b,
    0x06ea9e5d4383676a,
    0x3496e2e117e0ec80,
}};

/* (2^512)^2 mod p */
const fp r_squared_mod_p = {{
    0x36905b572ffc1724,
    0x67086f4525f1f27d,
    0x4faf3fbfd22370ca,
    0x192ea214bcc584b1,
    0x5dae03ee2f5de3d0,
    0x1e9248731776b371,
    0xad5f166e20e4f52d,
    0x4ed759aea6f3917e,
}};

/* -p^-1 mod 2^64 */
const uint64_t inv_min_p_mod_r = 0x66c1301f632e294d;

/* p - 2 */
const uint_c p_minus_2 = {{
    0x1b81b90533c6c879,
    0xc2721bf457aca835,
    0x516730cc1f0b4f25,
    0xa7aac6c567f35507,
    0x5afbfcc69322c9cd,
    0xb42d083aedc88c42,
    0xfc8ab0d15e3e4c4a,
    0x65b48e8f740f89bf,
}};

/* (p - 1) / 2 */
const uint_c p_minus_1_halves = {{
    0x8dc0dc8299e3643d,
    0xe1390dfa2bd6541a,
    0xa8b398660f85a792,
    0xd3d56362b3f9aa83,
    0x2d7dfe63499164e6,
    0x5a16841d76e44621,
    0xfe455868af1f2625,
    0x32da4747ba07c4df,
}};

/* floor(4 sqrt(p)) */
const uint_c four_sqrt_p = {{
    0x17895e71e1a20b3f,
    0x38d0cd95f8636a56,
    0x142b9541e59682cd,
    0x856f1399d91d6592,
    0x02,
}};

#endif
