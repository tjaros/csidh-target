
from copy import deepcopy
from fp import *

class Proj:
    def __init__(self, x = 0, z = 0) -> None:
        self.x = x
        self.z = z
    def __str__(self) -> str:
        return f"({self.x}, {self.z})"


def xDBLADD(R: Proj, S: Proj, P: Proj, Q: Proj, PQ: Proj, A24: Proj):
    tmp0, tmp1, tmp2 = Proj(), Proj(), Proj()
    tmp0 = fp_add(P.x, P.z)
    tmp1 = fp_sub(P.x, P.z)
    R.x = fp_sq(tmp0)
    tmp2 = fp_sub(Q.x, Q.z)
    S.x = fp_add(Q.x, Q.z)
    tmp0 = fp_mul(tmp0, tmp2)

    R.z = fp_sq(tmp1)
    tmp1 = fp_mul(tmp1, S.x)
    tmp2 = fp_sub(R.x, R.z)

    R.z = fp_mul(R.z, A24.z)

    R.x = fp_mul(R.x, R.z)
    S.k = fp_mul(A24.x, tmp2)

    S.z = fp_sub(tmp0, tmp1)
    R.z = fp_add(R.z, S.x)
    S.x = fp_add(tmp0, tmp1)
    R.z = fp_mul(R.z, tmp2)

    S.z = fp_sq(S.z)
    S.x = fp_sq(S.x)
    S.z = fp_mul(S.z, PQ.x)
    S.x = fp_mul(S.x, PQ.z)



def xDBL(Q: Proj, A: Proj, P: Proj):
    a, b, c = 0, 0, 0
    a = fp_add(P.x, P.z)
    a = fp_sq(a)
    b = fp_sub(P.x, P.z)
    b = fp_sq(b)
    c = fp_sub(a, b)
    b = fp_add(b, b)
    b = fp_add(b, b) #/* multiplication by 4 */
    b = fp_mul(b, A.z)
    Q.x = fp_mul(a, b)
    a = fp_add(A.z, A.z) #/* multiplication by 2 */
    a = fp_add(a, A.x)
    a = fp_mul(a, c)
    a =  fp_add(a, b)
    Q.z = fp_mul(a, c)

def xADD(S: Proj, P: Proj, Q: Proj, PQ: Proj):
    a, b, c, d = 0, 0, 0, 0
    a = fp_add(P.x, P.z)
    b = fp_sub(P.x, P.z)
    c = fp_add(Q.x, Q.z)
    d = fp_sub(Q.x, Q.z)
    a = fp_mul(a, d)
    b = fp_mul(b, c)
    c = fp_add(a, b)
    d = fp_sub(a, b)
    c = fp_sq(c)
    d = fp_sq(d)
    S.x = fp_mul(PQ.z, c)
    S.z = fp_mul(PQ.x, d)

def uint_bit(x, k):
    return 1 & (x >> k)

def xMUL(A: Proj, P: Proj, k: int):
    Q = Proj()
    R: Proj = deepcopy(P)
    A24 = Proj()
    Pcopy = deepcopy(P) #/* in case Q = P */

    Q.x = fp_1
    Q.z = fp_0

    A24.x = fp_add(A.z, A.z) #//precomputation of A24=(A+2C:4C)
    A24.z = fp_add(A24.x, A24.x)
    A24.x = fp_add(A24.x, A.x)

    i = 63

    while not uint_bit(k, i):
        i -= 1
    
    print(f"{i=}")

    while i >= 0:
        bit = uint_bit(k, i)

        if bit:
            T = deepcopy(Q)
            Q = deepcopy(R)
            R = T
        xDBLADD(Q, R, Q, R, Pcopy, A24)
        if bit:
            T = deepcopy(Q)
            Q = deepcopy(R)
            R = T
        i -= 1
        print(str(Q))
    return Q

if __name__ == '__main__':
    P = Proj(119, 1)
    A = Proj(0, fp_1)
    k = 1
    print(f"P={str(P)} A={str(A)} {k=} {str(xMUL(A, P, k))}")
