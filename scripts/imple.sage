p = 4 * 3 * 5 * 7 - 1
primes = [3, 5, 7]
Fp = GF(p)


def from_weierstrass(EC):
    a, b = EC.a4(), EC.a6()
    F = EC.base_field()
    PR = PolynomialRing(F, name="z")
    z = PR.gens()[0]
    roots = (z**3 + a*z + b).roots()
    assert len(roots) > 0
    alpha = roots[0][0]
    s = (3*alpha**2 + a).sqrt() ** (-1)
    return -3 * (-1)**s.is_square() * alpha * s


def to_weierstrass(A):
    B = 1
    a = (3 - A**2) * pow(3 * B**2, -1, p)
    b = (2 * A**3 - 9 * A) * pow(27 * B**3, -1, p)
    return EllipticCurve(Fp, [a, b])


def group_action(pub, priv):
    es = priv.copy()
    A = pub
    assert len(es) == len(primes)
    EC = to_weierstrass(A)
    while True:
        if all(e == 0 for e in es):
            break
        x = Fp(randint(1, p-1))
        r = Fp(x ** 3 + A * x ** 2 + x)
        s = kronecker_symbol(r, p)
        assert (2 * is_square(r)) - 1 == s
        I = [i for i, e in enumerate(es) if sign(e) == s]
        if len(I) == 0:
            continue
        if s == -1:
            EC = EC.quadratic_twist()
        while True:
            tmp = EC.random_element()
            if not tmp.is_zero():
                break
        x = tmp.xy()[0]
        t = prod([primes[i] for i in I])
        P = EC.lift_x(x)
        assert (p + 1) % t == 0
        Q = ((p + 1) // t) * P
        for i in I:
            assert t % primes[i] == 0
            R = (t // primes[i]) * Q
            if R.is_zero():
                continue
            phi = EC.isogeny(R)
            EC = phi.codomain()
            Q = phi(Q)
            assert t % primes[i] == 0
            t = t // primes[i]
            es[i] -= s
        if s == -1:
            EC = EC.quadratic_twist()
    return from_weierstrass(EC)


