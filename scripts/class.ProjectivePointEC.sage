class ProjectivePointEC(object):
    '''
    Class for defining projective point on Elliptic curves.
    
    '''
    def __init__ (self, x, y, z = 1, curve = None):
        self._curve = curve
        self._x = x
        self._y = y
        self._z = z
        self._coord = [self._x, self._y, self._z]
                    
    def __repr__(self):
        return "(%s : %s : %s)"%(self._x, self._y, self._z)
    def __eq__(self, otherP):
        if (self._z == otherP._z):
            return (self._x, self._y) == (otherP._x, otherP._y)
        else:
            return (self._x/self._z, self._y/self._z) == (otherP._x/otherP._z, otherP._y/otherP._z)
    def __getitem__(self, i):
        return self._coord[i]
    def __neg__(self):
        return ProjectivePointEC(self._x, -self._y, self._z, self._curve)
    def __add__(self, otherP):
        if not(self._curve == otherP._curve):
            raise VallueError("Not on the same curve")
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
            return ProjectivePointEC(x, y, 1, curve = self._curve)
    def x(self):
        return self._x
    def y(self):
        return self._y
    def z(self):
        return self._z
    def curve(self):
        return self._curve
    
    
    
    def transformZ(self, R = None):
        r"""
        Input: R is a field
        Output: Point with z-coordinate 1.
        """        
        if (self._z == 0):
            return ProjectivePointEC(self._x, self._y, self._z, self._curve)
        if (self._z != 1):
            if (R == None):
                x = self._x/self._z
                y = self._y/self._z
            else:
                x = R(self._x/self._z)
                y = R(self._y/self._z)
            return ProjectivePointEC( x, y, 1, self._curve)
        else:
            return ProjectivePointEC(self._x, self._y, 1, self._curve)
    
    
    
    
    def transformMF(self):
        r"""
        Output: Point in with MC form, i.e. with only xz-coordinate point.
        """
        return PointMC(self._x, self._y, self._z, self._curve)