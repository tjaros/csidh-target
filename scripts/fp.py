
p = 419
p_plus_one = p + 1
fp_0 = 0
fp_1 = 2**64 % p
r_squared_mod_p = fp_1 ** 2 % p
inv_min_p_mod_r = pow(p, -1, fp_1)

def fp_add(y, z):
    return (y + z) % p

def fp_sub(y, z):
    return (y - z) % p

def fp_sq(y):
    return pow(y, 2, p)

def fp_mul(y, z):
    return (y * z) % p




