class CSIDH:
    def __init__(self, p, primes, m):
        self.p = p
        self.m = m
        self.primes = primes
        self.Fp = GF(p)

    def get_public(self, private):
        """Computation of CSIDH public key

        We need to compute an Elliptic curve that is reached after
        $a_i$ isogenies of degree $l_i$ for $1 <= i <= r$

        We start at predefined curve $y^2 = x^3 + x$

        :private: secret exponent vector $(a_1, ..., a_r)$ for
        $a_i \in [-m, m]$
        :return: Elliptic curve represented by Montgomery coefficient
        """
        assert len(private) == len(self.primes)

        return self.group_action(0, private)

    def group_action(self, A, e):
        assert len(e) == len(self.primes)
        # We begin at the Elliptic curve y^2 = x^3 + A*x^2 + x
        # It should be validated that the curve is supersingular
        # before doing any computation. That could be apparently
        # done via sampling random points and checking that all
        # primes $l_i$ appear in group order, and/or using Hasse
        # interval
        E = EllipticCurve(self.Fp, [0, A, 0, 1, 0])
        # We loop until we have no more isogenies to perform,
        # that is if the vector e is zero.
        #
        # The reason we do all the isogenies of same sign should
        # be because of optimization reasons, we could always do it
        # in a way where we compute for each $l_i$-isogeny separately,
        # but here it is done so that we create a point T, of degree
        # prod(l_i having same sign in the exponent) and computing
        # with this point all the $l_i$-isogenies, thus spending
        # less time on finding points and doing scalar multiplications
        #
        # Apparently this computation was leaking a lot of information
        # and should have changed since then. Havent seen any actual
        # implementation yet since I'm just starting to study the topic
        while any([e_i != 0 for e_i in e]):
            x = self.Fp.random_element()
            s = 1 if self.Fp(x**3 + A*x**2 + x).is_square() else -1
            S = [i for i in range(len(e)) if e[i] != 0 and sign(e[i]) == s]

            if S == []:
                continue

            # For some reason, I saw some similar implementations
            # to compute in quadratic twist if the sign is negative
            # or just swapping it each time. Why? If you uncomment
            # them it wil work too since quadratic twist is
            # isomomorphism. The computation just ends up in different
            # curve with different j-invariant

            #if s == -1:
            #    E = E.quadratic_twist()

            P = E.random_element()
            while P.is_zero():
                P = E.random_element()

            k = prod([self.primes[i] for i in S])
            T = ((self.p + 1) // k) * P

            for i in S:
                assert k % self.primes[i] == 0

                R = (k // self.primes[i]) * T
                if R.is_zero():
                    continue
                phi = E.isogeny(R)
                E, T = phi.codomain(), phi(T)
                k = k // self.primes[i]
                e[i] = e[i] - s

            #if s == -1:
            #    E = E.quadratic_twist()
                

        return E.montgomery_model().a2()


if __name__ == '__main__':
    for _ in range(100):
        m = 5
        a = [randint(-m, m+1) for _ in range(3)]
        b = [randint(-m, m+1) for _ in range(3)]
        csidh = CSIDH(4 * 3 * 5 * 7 - 1, [3,5,7], 5)
        apub = csidh.get_public(a.copy())
        bpub = csidh.get_public(b.copy())
        #print(f"{apub=} {bpub=}")
        AliceShared = csidh.group_action(bpub, a.copy())
        BobShared = csidh.group_action(apub, b.copy())
        #print(f"{AliceShared=} {BobShared=}")
        assert AliceShared == BobShared
