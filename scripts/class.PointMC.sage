class PointMC(ProjectivePointEC):
    '''
    Class defining points on Montgomery curves in Fp.
    
    '''
    def __init__ (self, x, y = None, z = 1, curve = None):
        self._x = x
        self._y = y
        self._z = z
        self._curve = curve
    def __repr__(self):
        return "(%s : %s)"%(self._x, self._z)
    def __neg__(self):
        if (self._y != None):
            return PointMC(self._x, -self._y, self._z, self._curve)
        else:
            return PointMC(self._x, self._y, self._z, self._curve)
        
    def __eq__(self, otherP):
        if ((self._z == 0 and otherP._z != 0) \
            or (self._z != 0 and otherP._z == 0)):
            return False
        elif (self._z == otherP._z):
            return (self._x == otherP._x) \
                and (self._y == otherP._y or self._y == None or otherP._y == None)
        else:
            if (self._y != None and otherP._y != None):
                return (self._x/self._z, self._y/self._z) \
                    == (otherP._x/otherP._z, otherP._y/otherP._z)
            else:
                return (self._x/self._z) == (otherP._x/otherP._z)
    def __add__(self, otherP):
        '''
         Formula for adding.
         https://eprint.iacr.org/2017/212.pdf
         Costello
         '''
        if (self._y == None or otherP._y == None):
            raise ValueError("Use addAlgorithm()")
        elif not(self._curve == otherP._curve):
            raise ValueError("Not on the same curve")
        else:
            A = self._curve._coef
            R = self._curve._field
            if (self == -otherP):
                return ProjectivePointEC(R(0),R(1),R(0), self._curve)
            elif (self == otherP):
                lam = R((3*self._x^2 + 2*A*self._x + 1)/(2*(self._x^3 + A*self._x^2 + self._x)))    
            else:
                lam = R((otherP._y - self._y)/(otherP._x - self._x))
            x = R(lam^2 - (self._x + otherP._x) - A)
            y = R((2*self._x + otherP._x + A)*lam - lam^3 - self._y)
            return PointMC(x, y, 1, curve = self._curve)
        
        
    def x(self):
        return self._x
    def y(self):
        return self._y
    def z(self):
        return self._z
    def curve(self):
        return self._curve
###################################################
###################################################
###################################################    
    
    def transformZ(self):
        R = self._curve._field
        if (self._z == 0):
            return PointMC(R(0), R(1), R(0), self._curve)
        elif (self._z != 1):
            x = R(self._x / self._z)
            if (self._y != None):
                y = R(self._y / self._z)
                PointMC(x, y, 1, self._curve)
            else:
                return PointMC(x, None, 1, self._curve)
        else:
            return PointMC(self._x, self._y, 1, self._curve)

###################################################
###################################################
###################################################        
        
    def addAlgorithm(self, otherP, diff):
        r"""
        This addAlgorithm() is based on some properties of Montgomery curves. It can be used in the computation of [k]P, where P is a point on some elliptic curve in the Montgomery form.
        
        https://eprint.iacr.org/2017/212.pdf,
        Costello
        """
        R = self._curve._field
        if (diff._z == 0):
            return self.dblAlgorithm()
        elif (diff._x == 0 and diff._z == 1):
            raise ValueError("Diff point is of order 2")
            return PointMC(R(0),R(1),R(0), self._curve)
        else:
            v0 = self._x + self._z
            v1 = otherP._x - otherP._z
            v1 = v0*v1
            v0 = self._x - self._z
            v2 = otherP._x + otherP._z
            v2 = v0 * v2
            v3 = v1 + v2
            v3 = v3^2
            v4 = v1 - v2
            v4 = v4^2
            x = diff._z * v3
            z = diff._x * v4
            return PointMC(R(x), None, R(z), self._curve)

        
        ###################################################
###################################################
###################################################
    def dblAlgorithm(self):
        r"""
        This dblAlgorithm() is based on some properties of Montgomery curves. It can be used in the computation of [k]P, where P is a point on some elliptic curve in the Montgomery form.
        
        https://eprint.iacr.org/2017/212.pdf,
        Costello
        """
        A = self._curve._coef
        R = self._curve._field
        if (self._z == 0 or (self._x == 0 and self._z == 1)):
            return PointMC(R(0),R(1),R(0), self._curve)
        else:
            v1 = self._x + self._z
            v1 = v1^2
            v2 = self._x - self._z
            v2 = v2^2
            x = v1 * v2
            v1 = v1 - v2
            v3 = R((A + 2)/4)*v1
            v3 = v3 + v2
            z = v1 * v3
            return PointMC(R(x), None, R(z), self._curve)
###################################################
###################################################
###################################################

    def mLadder(self, k):
        r"""
        Computation of [k]P, where P is a point on some elliptic curve in the Montgomery form.
        
        https://eprint.iacr.org/2017/212.pdf,
        Costello
        """
        if not(isinstance(k, list) or isinstance(k,str)):
            k = Integer(k)
            k = k.digits(2)
        if (isinstance(k, list) or isinstance(k,str)):
            l = len(k)
            P0 = self
            P1 = self.dblAlgorithm()
            for i in range(0, l - 1):
                if (k[l-2-i] == 0):
                    (P0,P1) = (P0.dblAlgorithm(), P0.addAlgorithm(P1,self))
                else:
                    (P0, P1) = (P0.addAlgorithm(P1,self), P1.dblAlgorithm())
            return P0.transformZ()

        
        ###################################################
###################################################
###################################################
    def recoverY(self, point, add):
        r"""
        
        https://eprint.iacr.org/2017/212.pdf,
        Costello
        """
        ## https://eprint.iacr.org/2017/212.pdf Algorithm 5
        A = self._curve._coef
        R = self._curve._field
        v1 = point._x * self._z
        v2 = self._x + v1
        v3 = self._x - v1
        v3 = v3^2
        v3 = v3 * add._x
        v1 = 2 * A * self._z
        v2 = v2 + v1
        v4 = point._x * self._x
        v4 = v4 + self._z
        v2 = v2 * v4
        v1 = v1 * self._z
        v2 = v2- v1
        v2 = v2 * add._z
        y = v2 - v3
        v1 = 2 * point._y
        v1 = v1 * self._z
        v1 = v1 * add._z
        x = v1 * self._x
        z = v1 * self._z
        if (z != 0):
            return PointMC(R(x/z), R(y/z), R(1), self._curve)
        else:
            return PointMC(R(0), R(1), R(0), self._curve)
         