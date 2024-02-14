####################################################################################       
####################################################################################   

# For odd prime degree isogeny on Montgomery cures over Fp

####################################################################################       
#################################################################################### 

class IsogenyMC(MontgomeryCurve):
    def __init__(self, domain, codomain = None, kernel = None, baseDegree = None, exponent = 1):
        self._domain = domain
        self._codomain = codomain
        self._kernel = kernel
        self._baseDegree = baseDegree
        self._exponent = exponent
        self._degree = baseDegree^self._exponent
    def __repr__(self):
        s = "Isogeny of degree %s from Montgomery elliptic curve defined by y^2 = x^3 + "%self._degree
        if (self._domain._coef == 0):
            s += "x"
        else:
            s += "%s*x^2 + x"%self._domain._coef
        s += " over finite field of size %s to Montgomery elliptic curve defined by y^2 = x^3 + "%self._domain._prime
        if (self._codomain._coef == 0):
            s += "x"
        else:
            s += "%s*x^2 + x"%self._codomain._coef
        s += " over finite field of size %s."%self._codomain._prime
        return s
        
    def __call__(self, *arg, **kwarg):
        image = []
        point = arg[0]
        R = self._codomain._field
        d = (self._degree - 1)//2
        for i in range(1,d + 1):
            point1 = self._kernel.mLadder(i)
            if (R(point._x - point1._x) == 0):
                return PointMC(R(0),R(1),R(0),self._codomain)
                break
            else:
                t = R((point._x * point1._x - 1)/(point._x - point1._x))
                image.append(t)
        
        if (image != []):
            image = R(point._x * product(image)^2)
            return (self._codomain).lift_x(image, MF = True)
    
    def domain(self):
        return self._domain
    def codomain(self):
        return self._codomain
    def kernel(self):
        return self._kernel
    def degree(self):
        return self._degree

    ####################################################################################       
####################################################################################   

# For odd prime degree isogeny on Montgomery cures over Fp using SQRT-Velu

####################################################################################       
#################################################################################### 
class IsogenyMC_sqrt(MontgomeryCurve):
    def __init__(self, domain, codomain = None, kernel = None, baseDegree = None, exponent = 1):
        self._domain = domain
        self._codomain = codomain
        self._kernel = kernel
        self._baseDegree = baseDegree
        self._exponent = exponent
        self._degree = baseDegree^self._exponent
    def __repr__(self):
        s = "Isogeny of degree %s from Montgomery elliptic curve defined by y^2 = x^3 + "%self._degree
        if (self._domain._coef == 0):
            s += "x"
        else:
            s += "%s*x^2 + x"%self._domain._coef
        s += " over finite field of size %s to Montgomery elliptic curve defined by y^2 = x^3 + "%self._domain._prime
        if (self._codomain._coef == 0):
            s += "x"
        else:
            s += "%s*x^2 + x"%self._codomain._coef
        s += " over finite field of size %s."%self._codomain._prime
        return s
        
    def __call__(self, *arg, **kwarg):
        if (self._degree.is_prime()) and (self._degree % 2) != 0:
            point = arg[0]
            I = arg[1]
            J = arg[2]
            K = arg[3]
            m = arg[4]
            
            R = self._domain._field
            A = self._domain._coef
            l = self._degree
            kX.<X> = R[]
            
            def F0(X1,X2):
                return (X1-X2)^2

            def F1(X1,X2):
                return -2*((X1*X2+1)*(X1+X2)+2*A*X1*X2)

            def F2(X1,X2):
                return (X1*X2-1)^2
     

            hKP = prod(point._x-m[s] for s in K)
            hI = kX(1)
            for i in I:                           
                hI = kX(hI)._mul_karatsuba(X-m[i])
#             DJ = kX(prod(F0(X,m[j]) for j in J))
            DJ = kX(1)
            EJ = kX(1)
            for j in J:                           
                DJ = kX(DJ)._mul_karatsuba(F0(X,m[j]))
                EJ = kX(EJ)._mul_karatsuba(F0(X,m[j])*point._x^2+F1(X,m[j])*point._x+F2(X,m[j]))
            DeltaIJ = hI.resultant(DJ)
            
#             EJ = kX(prod(F0(X,m[j])*point._x^2+F1(X,m[j])*point._x+F2(X,m[j]) for j in J))
            T = hI.resultant(EJ)
  
            image = R(hKP*T/DeltaIJ)
    
            hKP = prod(1/point._x-m[s] for s in K)
            hI = kX(1)
            for i in I:                           
                hI = kX(hI)._mul_karatsuba(X-m[i])
            DJ = kX(1)
            EJ = kX(1)
            for j in J:                           
                DJ = kX(DJ)._mul_karatsuba(F0(X,m[j]))
                EJ = kX(EJ)._mul_karatsuba(F0(X,m[j])*point._x^(-2)+F1(X,m[j])*point._x^(-1)+F2(X,m[j]))
            DeltaIJ = hI.resultant(DJ)
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