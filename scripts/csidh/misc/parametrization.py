from functools import reduce
from math import floor, sqrt


def integer_to_uint64_array(value):
    if value <= 0:
        raise ValueError("Input must be a positive integer")

    uint64_array = []

    while value > 0:
        uint64_array.append(value % 2**64)
        value = value >> 64

    return uint64_array

def uint64_array_to_integer(uint64_array):
    if not uint64_array:
        raise ValueError("Input array must not be empty")

    value = 0
    for i in range(len(uint64_array)):
        value += uint64_array[i] << (64 * i)

    return value


def print_as_var(name, array, brackets=True, semicolon=True):
    if name:
        print(f"{name} = ", end="")

    if brackets:
        print("{{", end="\n    ")

    for i, num in enumerate(array):
        print(f"0x{num:016x}", end=", " if i < len(array) - 1 else "")

    if brackets:
        print("\n}}", end="")

    if semicolon:
        print(";\n")
    else:
        print(",\n")


def compute_constants(primes, limbs, batches):
    p = 4 * reduce(lambda x, y: x * y, primes) - 1
    print_as_var("const uint_c p", integer_to_uint64_array(p))
    print_as_var("const uint_c p_plus_one", integer_to_uint64_array(p + 1))

    print("const fp fp_0 = {{0}};\n")
    # scaling factor 2**{limbs * 64} % p
    bits = 64 * limbs
    print(f"/* scaling factor 2^{bits} mod p*/")
    print_as_var("const fp fp_1", integer_to_uint64_array(pow(2, bits, p)))

    # square of scaling factor
    print(f"/* (2^{bits})^2 mod  p */")
    print_as_var(
        "const fp r_squared_mod_p", integer_to_uint64_array(pow(2, bits * 2, p))
    )

    # inversion of -p modulo 2**64
    print_as_var(
        "const uint64_t inv_min__mod_r",
        integer_to_uint64_array(pow(-p, -1, 2**64)),
        False,
    )

    # self explanatory
    print_as_var("const uint_c p_minus_2", integer_to_uint64_array(p - 2))
    print_as_var("const uint_c p_minus_1_halves", integer_to_uint64_array((p - 1) // 2))

    # The square root * 4 is different comp. to their implementation
    # only used for validation which is useless for us
    # print_as_var('const uint_c four_sqrt_p', integer_to_uint64_array(floor(4*sqrt(p))))

    # Could not reproduce the original batches, but in reduced Fp we just need one batch
    m = batches
    print("/* SIMBA prime batches")
    S = [
        [i + xm for xm in range(0, len(primes), m) if i + xm < len(primes)]
        for i in range(m)
    ]
    for S_i in S:
        print(S_i)
    print("*/")
    print(f"uint_c k[{m}] = {{")
    for S_i in S:
        batch = [primes[i] for i in S_i]
        k_i = reduce(lambda x, y: x * y, batch)
        print_as_var(None, integer_to_uint64_array(k_i), brackets=True, semicolon=False)
    print("};")
    # p order ? what the fuck is that


def parametrize_csidh_512():
    NUM_PRIMES = 74
    primes = [
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
    ]
    assert len(primes) == NUM_PRIMES

    compute_constants(primes, 8, 3)


def parametrize_csidh_f419():
    NUM_PRIMES = 3
    primes = [3, 5, 7]

    compute_constants(primes, 1, 1)


if __name__ == "__main__":
    parametrize_csidh_f419()
