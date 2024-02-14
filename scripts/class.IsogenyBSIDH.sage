# ####################################################################################       
# ####################################################################################   

# # Isogenies with odd prime degrees.

# ####################################################################################       
# #################################################################################### 

class IsogenyBSIDH(object):
    '''
    Class of odd-degree isogenies on Montgomery curves.
    
    For evalution of point using https://eprint.iacr.org/2019/843.pdf algorithm  from 2.2.
    
    '''
    def __init__(self, domain, codomain = None, kernel = None, baseDegree = None, exponent = 1):
        self._domain = domain
        self._codomain = codomain
        self._kernel = kernel
        self._baseDegree = baseDegree
        self._exponent = exponent
        self._degree = baseDegree^self._exponent
    def __repr__(self):
        s = "Isogeny of degree %s from Montgomery elliptic curve defined by "%self._degree
        if (self._domain._coef2 == 1):
            s += "y^2 = x^3 + "
        else:
            s += "(%s)*y^2 = x^3 + "%self._domain._coef2
        if (self._codomain._coef1 == 0):
            s += "x "
        elif (self._codomain._coef1 == 1):
            s += "x^2 + x "
        else:
            s += "(%s)*x^2 + x "%self._codomain._coef1
        s += " over finite field of size %s^%s to Montgomery elliptic curve defined by "%(self._codomain._prime,2)
        if (self._domain._coef2 == 1):
            s += "y^2 = x^3 + "
        else:
            s += "(%s)*y^2 = x^3 + "%self._domain._coef2
            
        if (self._codomain._coef1 == 0):
            s += "x "
        elif (self._codomain._coef1 == 1):
            s += "x^2 + x "
        else:
            s += "(%s)*x^2 + x "%self._codomain._coef1
        s += " over finite field of size %s^%s."%(self._codomain._prime,2)
        return s
        
    def __call__(self, *arg, **kwarg):
        if (self._degree.is_prime()) and (self._degree % 2) != 0:
            image = []
            point = arg[0]
            R = self._codomain._field
            d = (self._degree - 1)//2
            for i in range(1,d + 1):
                point1 = self._kernel.mLadder(i)
                if (R(point._x - point1._x) == 0):
                    return PointMCFp2(R(0),R(1),R(0),self._codomain)
                    break
                else:
                    t = R((point._x * point1._x - 1)/(point._x - point1._x))
                    image.append(t)
            if (image != []):
                image = R(point._x * product(image)^2)
                return (self._codomain).lift_xBSIDH(image)
        elif (self._degree % 2) != 0:
            [phiA, points] = self._domain.isogenyDecomposeBSIDH(self._degree.prime_factors()[0:len(LB.prime_factors())], self._kernel, arg)
            return points[0]
    
    
    def domain(self):
        return self._domain
    def codomain(self):
        return self._codomain
    def kernel(self):
        return self._kernel
    def degree(self):
        return self._degree
 
 ####################################################################################       
# ####################################################################################   

# # Isogenies with odd prime degrees with precomputations of s*kernel

# ####################################################################################       
# #################################################################################### 

class IsogenyBSIDH_pre(object):
    '''
    Class of odd-degree isogenies on Montgomery curves.
    
    For evalution of point using https://eprint.iacr.org/2019/843.pdf algorithm  from 2.2.
    
    '''
    def __init__(self, domain, codomain = None, kernel = None, baseDegree = None, exponent = 1):
        self._domain = domain
        self._codomain = codomain
        self._kernel = kernel
        self._baseDegree = baseDegree
        self._exponent = exponent
        self._degree = baseDegree^self._exponent
    def __repr__(self):
        s = "Isogeny of degree %s from Montgomery elliptic curve defined by "%self._degree
        if (self._domain._coef2 == 1):
            s += "y^2 = x^3 + "
        else:
            s += "(%s)*y^2 = x^3 + "%self._domain._coef2
        if (self._codomain._coef1 == 0):
            s += "x "
        elif (self._codomain._coef1 == 1):
            s += "x^2 + x "
        else:
            s += "(%s)*x^2 + x "%self._codomain._coef1
        s += " over finite field of size %s^%s to Montgomery elliptic curve defined by "%(self._codomain._prime,2)
        if (self._domain._coef2 == 1):
            s += "y^2 = x^3 + "
        else:
            s += "(%s)*y^2 = x^3 + "%self._domain._coef2
            
        if (self._codomain._coef1 == 0):
            s += "x "
        elif (self._codomain._coef1 == 1):
            s += "x^2 + x "
        else:
            s += "(%s)*x^2 + x "%self._codomain._coef1
        s += " over finite field of size %s^%s."%(self._codomain._prime,2)
        return s
        
    def __call__(self, *arg, **kwarg):
        if (self._degree.is_prime()) and (self._degree % 2) != 0:
            image = []
            point = arg[0]
            m = arg[1]
            R = self._codomain._field
            d = (self._degree - 1)//2
            for i in range(1,d + 1):
                point1 = m[i]
                if (R(point._x - point1._x) == 0):
                    return PointMCFp2(R(0),R(1),R(0),self._codomain)
                    break
                else:
                    t = R((point._x * point1._x - 1)/(point._x - point1._x))
                    image.append(t)
            if (image != []):
                image = R(point._x * product(image)^2)
                return (self._codomain).lift_xBSIDH(image)
        elif (self._degree % 2) != 0:
            [phiA, points] = self._domain.isogenyDecomposeBSIDH(self._degree.prime_factors()[0:len(LB.prime_factors())], self._kernel, arg)
            return points[0]
    
    
    def domain(self):
        return self._domain
    def codomain(self):
        return self._codomain
    def kernel(self):
        return self._kernel
    def degree(self):
        return self._degree
    
 # ####################################################################################       
# ####################################################################################   

# # Isogenies with odd prime degrees, SQRT-Velu, 


# ####################################################################################       
# ####################################################################################    
    
class IsogenyBSIDH_sqrt(object):
    '''
    Class of odd-degree isogenies on Montgomery curves.
    https://velusqrt.isogeny.org/velusqrt-20200616.pdf
    I,J,K is precomputed
    m = {s: kernel.mLadder(s)._x for s in S} is precomputed   
    '''
    def __init__(self, domain, codomain = None, kernel = None, baseDegree = None, exponent = 1):
        self._domain = domain
        self._codomain = codomain
        self._kernel = kernel
        self._baseDegree = baseDegree
        self._exponent = exponent
        self._degree = baseDegree^self._exponent
    def __repr__(self):
        s = "Isogeny of degree %s from Montgomery elliptic curve defined by "%self._degree
        if (self._domain._coef2 == 1):
            s += "y^2 = x^3 + "
        else:
            s += "(%s)*y^2 = x^3 + "%self._domain._coef2
        if (self._codomain._coef1 == 0):
            s += "x "
        elif (self._codomain._coef1 == 1):
            s += "x^2 + x "
        else:
            s += "(%s)*x^2 + x "%self._codomain._coef1
        s += " over finite field of size %s^%s to Montgomery elliptic curve defined by "%(self._codomain._prime,2)
        if (self._domain._coef2 == 1):
            s += "y^2 = x^3 + "
        else:
            s += "(%s)*y^2 = x^3 + "%self._domain._coef2
            
        if (self._codomain._coef1 == 0):
            s += "x "
        elif (self._codomain._coef1 == 1):
            s += "x^2 + x "
        else:
            s += "(%s)*x^2 + x "%self._codomain._coef1
        s += " over finite field of size %s^%s."%(self._codomain._prime,2)
        return s
        
    def __call__(self, *arg, **kwarg):
        '''
        Evauation of isogeny.
        https://velusqrt.isogeny.org/velusqrt-20200616.pdf
        '''             
        if (self._degree.is_prime()) and (self._degree % 2) != 0:
            point = arg[0]
            I = arg[1]
            J = arg[2]
            K = arg[3]
            m = arg[4]
            hI = arg[5]
            DJ = arg[6]
            DeltaIJ = arg[7]

            R = self._domain._field
            A = self._domain._coef1
            l = self._degree
            kX.<X> = R[]

            def F0(X1,X2):
                return (X1-X2)^2

            def F1(X1,X2):
                return -2*((X1*X2+1)*(X1+X2)+2*A*X1*X2)

            def F2(X1,X2):
                return (X1*X2-1)^2


            hKP = prod(point._x-m[s] for s in K)
            EJ = kX(prod(F0(X,m[j])*point._x^2+F1(X,m[j])*point._x+F2(X,m[j]) for j in J))
            T = hI.resultant(EJ)

            image = R(hKP*T/DeltaIJ)

            hKP = prod(1/point._x-m[s] for s in K)
            EJ = kX(prod(F0(X,m[j])*point._x^(-2)+F1(X,m[j])*point._x^(-1)+F2(X,m[j]) for j in J))
            T = hI.resultant(EJ)
            image2 = R(hKP*T/DeltaIJ)

            im = point._x^l*(image2)^2/(image)^2
            return (self._codomain).lift_x(im)

        else:
            raise ValueError('Kernel has order 2.')
    
    def domain(self):
        return self._domain
    def codomain(self):
        return self._codomain
    def kernel(self):
        return self._kernel
    def degree(self):
        return self._degree

def F0(X1,X2):
    return (X1-X2)^2

def F1(X1,X2,a):
    return -2*((X1*X2+1)*(X1+X2)+2*a*X1*X2)

def F2(X1,X2):
    return (X1*X2-1)^2