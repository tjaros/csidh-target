class IsogenyEC(object):
    '''
    Isogeny from Edwards curves.
    
    using w coordinates
    
    https://eprint.iacr.org/2019/843.pdf
    '''
    def __init__(self, domain, codomain = None, kernel = None, degree = None):
        self._domain = domain
        self._codomain = codomain
        self._kernel = kernel
        self._degree = degree
    def __repr__(self):
        s = "Isogeny from Edward elliptic curve of degree %s defined by x^2 + y^2 = 1 + %s*x^2y^2 over finite field of size %s "%(self._degree, self._domain._coef1, self._domain._field)
        s += "to Edward elliptic curve defined by x^2 + y^2 = 1 + %s*x^2y^2 over finite field of size %s."%(self._codomain._coef1, self._codomain._field)
        return s
    
    def __call__(self, *arg, **kwarg):
        point = arg[0]
        R = self._domain._field
        kernel = self._kernel
        s = (self._degree-1)/2
        
        K = 1
        L = 1
        for i in range(1, s + 1):
            point1 = kernel.eLadder(i)
            K = K * (point._z * point1._w - point1._z * point._w)^2
            L = L * (point._w * point1._w - point._z * point1._z)^2
        w = point._w * K
        z = point._z * L
        return PointEdCW(w, z, self._codomain)
    
    def domain(self):
        return self._domain
    def codomain(self):
        return self._codomain
    def kernel(self):
        return self._kernel
    def degree(self):
        return self._degree