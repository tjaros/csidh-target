    
####################################################################################       
####################################################################################   

# Isogenies for SIKE 2 isogenies

####################################################################################       
####################################################################################    

class IsogenySIKE2(object):
    '''
    Class of 2-degree isogenies on Montgomery curves.
    
    SIKE file https://sike.org/files/SIDH-spec.pdf, Algorithm 11, 12
    
    For evalution of point using  SIKE official document, Algorithm 12 
    
    '''
    def __init__(self, domain, codomain = None, kernel = None, exponent = 1):
        self._domain = domain
        self._codomain = codomain
        self._kernel = kernel
        self._baseDegree = 2
        self._exponent = exponent
        self._degree = 2^self._exponent
    def __repr__(self):
        s = "Isogeny of degree %s^%s from "%(self._baseDegree, self._exponent)
        s += "Montgomery elliptic curve defined by "
        #----------------------------------------------
        if (self._domain._coef2 == 1):
            s += "y^2 = x^3 + "
        else:
            s += "(%s)*y^2 = x^3 + "%self._domain._coef2
        #----------------------------------------------   
        if (self._domain._coef1 == 0):
            s += "x "
        elif (self._domain._coef1 == 1):
            s += "x^2 + x "
        else:
            s += "(%s)*x^2 + x "%self._domain._coef1
        s += " over finite field of size %s^2 to Montgomery elliptic curve defined by "%self._domain._prime
        #----------------------------------------------
        if (self._codomain._coef2 == 1):
            s += "y^2 = x^3 + "
        else:
            s += "(%s)*y^2 = x^3 + "%self._codomain._coef2
        #----------------------------------------------   
        if (self._codomain._coef1 == 0):
            s += "x "
        elif (self._codomain._coef1 == 1):
            s += "x^2 + x "
        else:
            s += "(%s)*x^2 + x "%self._codomain._coef1
        s += " over finite field of size %s^2."%self._codomain._prime
        
       
        return s
        
    def __call__(self, *arg, **kwarg):
        # SIKE official document, Algorithm 10
        point = arg[0]
        R = self._codomain._field
        kernel = self._kernel
        t0 = kernel._x + kernel._z
        t1 = kernel._x - kernel._z
        t2 = point._x + point._z
        t3 = point._x - point._z
        t0 = t0 * t3
        t1 = t1 * t2
        t2 = t0 + t1
        t3 = t0 - t1
        x = point._x * t2
        z = point._z * t3
        P = PointMCFp2(R(x), None, R(z), self._codomain)
        return P.transformZ()
            
    def domain(self):
        return self._domain
    def codomain(self):
        return self._codomain
    def kernel(self):
        return self._kernel
    def baseDegree(self):
        return self._baseDegree
    def degree(self):
        return self._degree
    
    
    
####################################################################################       
####################################################################################   

# Isogenies for SIKE 4 isogenies


####################################################################################       
####################################################################################    
class IsogenySIKE4(object):
    '''
    Class of 4-degree isogenies on Montgomery curves.
    
    SIKE file https://sike.org/files/SIDH-spec.pdf, Algorithm 13,14
    
    For evalution of point using  SIKE official document, Algorithm 14
    
    '''
    def __init__(self, domain, codomain = None, kernel = None, exponent = 1):
        self._domain = domain
        self._codomain = codomain
        self._kernel = kernel
        self._baseDegree = 4
        self._exponent = exponent
        self._degree = 2^self._exponent
    def __repr__(self):
        s = "Isogeny of degree %s^%s from "%(self._baseDegree, self._exponent)
        s += "Montgomery elliptic curve defined by "
        #----------------------------------------------
        if (self._domain._coef2 == 1):
            s += "y^2 = x^3 + "
        else:
            s += "(%s)*y^2 = x^3 + "%self._domain._coef2
        #----------------------------------------------   
        if (self._domain._coef1 == 0):
            s += "x "
        elif (self._domain._coef1 == 1):
            s += "x^2 + x "
        else:
            s += "(%s)*x^2 + x "%self._domain._coef1
        s += " over finite field of size %s^2 to Montgomery elliptic curve defined by "%self._domain._prime
        #----------------------------------------------
        if (self._codomain._coef2 == 1):
            s += "y^2 = x^3 + "
        else:
            s += "(%s)*y^2 = x^3 + "%self._codomain._coef2
        #----------------------------------------------   
        if (self._codomain._coef1 == 0):
            s += "x "
        elif (self._codomain._coef1 == 1):
            s += "x^2 + x "
        else:
            s += "(%s)*x^2 + x "%self._codomain._coef1
        s += " over finite field of size %s^2."%self._codomain._prime
        
        return s
        
    def __call__(self, *arg, **kwarg):
        # SIKE official document, Algorithm 10
        point = arg[0]
        R = self._codomain._field
        kernel = self._kernel
        k2 = kernel._x - kernel._z
        k3 = kernel._x + kernel._z
        k1 = kernel._z^2
        k1 = k1 + k1
        k1 = k1 + k1
        t0 = point._x + point._z
        t1 = point._x - point._z
        xx = t0 * k2
        zz = t1 * k3
        t0 = t0 * t1
        t0 = t0 * k1
        t1 = xx + zz
        zz = xx - zz
        t1 = t1^2
        zz = zz^2
        xx = t0 + t1
        t0 = zz - t0
        x = xx * t1
        z = zz * t0
        P = PointMCFp2(R(x), None, R(z), self._codomain)
        return P.transformZ()
            
    def domain(self):
        return self._domain
    def codomain(self):
        return self._codomain
    def kernel(self):
        return self._kernel
    def baseDegree(self):
        return self._baseDegree
    def degree(self):
  
    
####################################################################################       
####################################################################################   

# Isogenies wfor SIKE 3 isogeny

####################################################################################       
####################################################################################    

class IsogenySIKE3(object):
    '''
    Class of 3-degree isogenies on Montgomery curves.
    
    SIKE file https://sike.org/files/SIDH-spec.pdf, Algorithm 15,16
    
    For evalution of point using  SIKE official document, Algorithm 16 
    
    '''
    def __init__(self, domain, codomain = None, kernel = None, exponent = 1):
        self._domain = domain
        self._codomain = codomain
        self._kernel = kernel
        self._baseDegree = 3
        self._exponent = exponent
        self._degree = 3^self._exponent
        
    def __repr__(self):
        s = "Isogeny of degree %s^%s from "%(self._baseDegree, self._exponent)
        s += "Montgomery elliptic curve defined by "
        #----------------------------------------------
        if (self._domain._coef2 == 1):
            s += "y^2 = x^3 + "
        else:
            s += "(%s)*y^2 = x^3 + "%self._domain._coef2
        #----------------------------------------------   
        if (self._domain._coef1 == 0):
            s += "x "
        elif (self._domain._coef1 == 1):
            s += "x^2 + x "
        else:
            s += "(%s)*x^2 + x "%self._domain._coef1
        s += " over finite field of size %s^2 to Montgomery elliptic curve defined by "%self._domain._prime
        #----------------------------------------------
        if (self._codomain._coef2 == 1):
            s += "y^2 = x^3 + "
        else:
            s += "(%s)*y^2 = x^3 + "%self._codomain._coef2
        #----------------------------------------------   
        if (self._codomain._coef1 == 0):
            s += "x "
        elif (self._codomain._coef1 == 1):
            s += "x^2 + x "
        else:
            s += "(%s)*x^2 + x "%self._codomain._coef1
        s += " over finite field of size %s^2."%self._codomain._prime
        
       
        return s
        
    def __call__(self, *arg, **kwarg):
        # SIKE official document, Algorithm 10
        point = arg[0]
        R = self._codomain._field
        kernel = self._kernel
        t0 = point._x + point._z
        t1 = point._x - point._z
        K1 = kernel._x - kernel._z
        t0 = K1 * t0
        K2 = kernel._x + kernel._z
        t1 = K2 * t1
        t2 = t0 + t1
        t0 = t1 - t0
        t2 = t2^2
        t0 = t0^2
        x = point._x * t2
        z = point._z * t0
        P = PointMCFp2(R(x), None, R(z), self._codomain)
        return P.transformZ()
    
    def domain(self):
        return self._domain
    def codomain(self):
        return self._codomain
    def kernel(self):
        return self._kernel
    def baseDegree(self):
        return self._baseDegree
    def degree(self):
        return self._degree

    
####################################################################################       
####################################################################################   

# Isogenies for e-SIDH 5-isogenies.

####################################################################################       
####################################################################################        
    
class IsogenySIKE5(object):
    '''
    Class of 5-degree isogenies on Montgomery curves.
    
    '''
    def __init__(self, domain, codomain = None, kernel = None, exponent = 1):
        self._domain = domain
        self._codomain = codomain
        self._kernel = kernel
        self._baseDegree = 5
        self._exponent = exponent
        self._degree = 5^self._exponent
        
    def __repr__(self):
        s = "Isogeny of degree %s^%s from "%(self._baseDegree, self._exponent)
        s += "Montgomery elliptic curve defined by "
        #----------------------------------------------
        if (self._domain._coef2 == 1):
            s += "y^2 = x^3 + "
        else:
            s += "(%s)*y^2 = x^3 + "%self._domain._coef2
        #----------------------------------------------   
        if (self._domain._coef1 == 0):
            s += "x "
        elif (self._domain._coef1 == 1):
            s += "x^2 + x "
        else:
            s += "(%s)*x^2 + x "%self._domain._coef1
        s += " over finite field of size %s^2 to Montgomery elliptic curve defined by "%self._domain._prime
        #----------------------------------------------
        if (self._codomain._coef2 == 1):
            s += "y^2 = x^3 + "
        else:
            s += "(%s)*y^2 = x^3 + "%self._codomain._coef2
        #----------------------------------------------   
        if (self._codomain._coef1 == 0):
            s += "x "
        elif (self._codomain._coef1 == 1):
            s += "x^2 + x "
        else:
            s += "(%s)*x^2 + x "%self._codomain._coef1
        s += " over finite field of size %s^2."%self._codomain._prime
        
       
        return s
        
    def domain(self):
        return self._domain
    def codomain(self):
        return self._codomain
    def kernel(self):
        return self._kernel
    def baseDegree(self):
        return self._baseDegree
    def degree(self):
        return self._degree

## in file IsogenyBSIDH.sage    
# ####################################################################################       
# ####################################################################################   

# # Isogenies with odd prime degrees.

# ####################################################################################       
# ####################################################################################      
    
    
# class IsogenyBSIDH(object):
#     '''
#     Class of odd-degree isogenies on Montgomery curves.
    
#     For evalution of point using https://eprint.iacr.org/2019/843.pdf algorithm  from 2.2.
    
#     '''
#     def __init__(self, domain, codomain = None, kernel = None, baseDegree = None, exponent = 1):
#         self._domain = domain
#         self._codomain = codomain
#         self._kernel = kernel
#         self._baseDegree = baseDegree
#         self._exponent = exponent
#         self._degree = baseDegree^self._exponent
#     def __repr__(self):
#         s = "Isogeny of degree %s from Montgomery elliptic curve defined by "%self._degree
#         if (self._domain._coef2 == 1):
#             s += "y^2 = x^3 + "
#         else:
#             s += "(%s)*y^2 = x^3 + "%self._domain._coef2
#         if (self._codomain._coef1 == 0):
#             s += "x "
#         elif (self._codomain._coef1 == 1):
#             s += "x^2 + x "
#         else:
#             s += "(%s)*x^2 + x "%self._codomain._coef1
#         s += " over finite field of size %s^%s to Montgomery elliptic curve defined by "%(self._codomain._prime,2)
#         if (self._domain._coef2 == 1):
#             s += "y^2 = x^3 + "
#         else:
#             s += "(%s)*y^2 = x^3 + "%self._domain._coef2
            
#         if (self._codomain._coef1 == 0):
#             s += "x "
#         elif (self._codomain._coef1 == 1):
#             s += "x^2 + x "
#         else:
#             s += "(%s)*x^2 + x "%self._codomain._coef1
#         s += " over finite field of size %s^%s."%(self._codomain._prime,2)
#         return s
        
#     def __call__(self, *arg, **kwarg):
#         if (self._degree.is_prime()) and (self._degree % 2) != 0:
#             image = []
#             point = arg[0]
#             R = self._codomain._field
#             d = (self._degree - 1)//2
#             for i in range(1,d + 1):
#                 point1 = self._kernel.mLadder(i)
#                 if (R(point._x - point1._x) == 0):
#                     return PointMCFp2(R(0),R(1),R(0),self._codomain)
#                     break
#                 else:
#                     t = R((point._x * point1._x - 1)/(point._x - point1._x))
#                     image.append(t)
        
#             if (image != []):
#                 image = R(point._x * product(image)^2)
#                 return (self._codomain).lift_xBSIDH(image)
#         elif (self._degree % 2) != 0:
#             [phiA, points] = self._domain.isogenyDecomposeBSIDH(self._degree.prime_factors()[0:len(LB.prime_factors())], self._kernel, arg)
#             return points[0]
# #     def __call__(self, *arg, **kwarg):
# #         if (self._degree.is_prime()) and (self._degree % 2) != 0:
# #             image = []
# #             image2 = []
# #             point = arg[0]
# #             t0 = point._x - 1
# #             R = self._codomain._field
# #             d = (self._degree - 1)//2
# #             for i in range(1,d + 1):
# #                 point1 = self._kernel.mLadder(i)
# #                 if (R(point._x - point1._x) == 0):
# #                     return PointMCFp2(R(0),R(1),R(0),self._codomain)
# #                     break
# #                 else:
# #                     m = t0 * (point1._x + 1)
# #                     n = 2 * (point1._x - 1) 
# #                     image.append(m+n)
# #                     image2.append(m-n)
        
# #             if (image != []):
# #                 image = R(point._x * product(image)^2)
# #                 image2 = R(product(image2)^2)
# #                 image = image/image2
# #                 return (self._codomain).lift_xBSIDH(image)
# #         elif (self._degree % 2) != 0:
# #             [phiA, points] = self._domain.isogenyDecomposeBSIDH(self._degree.prime_factors()[0:len(LB.prime_factors())], self._kernel, arg)
# #             return points[0]
    
#     def domain(self):
#         return self._domain
#     def codomain(self):
#         return self._codomain
#     def kernel(self):
#         return self._kernel
#     def degree(self):
#         return self._degree
    
# ####################################################################################       
# ####################################################################################   

# # For using SQRT-Velus formulas on Montgmery over Fp2

# ####################################################################################       
# ####################################################################################  
    
# class IsogenyBSIDH_sqrt(object):
#     def __init__(self, domain, codomain = None, kernel = None, baseDegree = None, exponent = 1):
#         self._domain = domain
#         self._codomain = codomain
#         self._kernel = kernel
#         self._baseDegree = baseDegree
#         self._exponent = exponent
#         self._degree = baseDegree^self._exponent
#     def __repr__(self):
#         s = "Isogeny of degree %s from Montgomery elliptic curve defined by "%self._degree
#         if (self._domain._coef2 == 1):
#             s += "y^2 = x^3 + "
#         else:
#             s += "(%s)*y^2 = x^3 + "%self._domain._coef2
#         if (self._codomain._coef1 == 0):
#             s += "x "
#         elif (self._codomain._coef1 == 1):
#             s += "x^2 + x "
#         else:
#             s += "(%s)*x^2 + x "%self._codomain._coef1
#         s += " over finite field of size %s^%s to Montgomery elliptic curve defined by "%(self._codomain._prime,2)
#         if (self._domain._coef2 == 1):
#             s += "y^2 = x^3 + "
#         else:
#             s += "(%s)*y^2 = x^3 + "%self._domain._coef2
            
#         if (self._codomain._coef1 == 0):
#             s += "x "
#         elif (self._codomain._coef1 == 1):
#             s += "x^2 + x "
#         else:
#             s += "(%s)*x^2 + x "%self._codomain._coef1
#         s += " over finite field of size %s^%s."%(self._codomain._prime,2)
#         return s
        
#     def __call__(self, *arg, **kwarg):
#         if (self._degree.is_prime()) and (self._degree % 2) != 0:
#             point = arg[0]
#             I = arg[1]
#             J = arg[2]
#             K = arg[3]
#             m = arg[4]
            
#             R = self._domain._field
#             A = self._domain._coef1
#             l = self._degree
#             kX.<X> = R[]
            
#             def F0(X1,X2):
#                 return (X1-X2)^2

#             def F1(X1,X2):
#                 return -2*((X1*X2+1)*(X1+X2)+2*A*X1*X2)

#             def F2(X1,X2):
#                 return (X1*X2-1)^2
     

#             hKP = prod(point._x-m[s] for s in K)
                                    
#             hI = kX(prod(X-m[i] for i in I))
#             DJ = kX(prod(F0(X,m[j]) for j in J))
# #             DJ = kX(1)
# #             EJ = kX(1)
# #             for j in J:                           
# #                 DJ = kX(DJ)._mul_karatsuba(F0(X,m[j]))
# #                 EJ = kX(EJ)._mul_karatsuba(F0(X,m[j])*point._x^2+F1(X,m[j])*point._x+F2(X,m[j]))
#             DeltaIJ = hI.resultant(DJ)
            
#             EJ = kX(prod(F0(X,m[j])*point._x^2+F1(X,m[j])*point._x+F2(X,m[j]) for j in J))
#             T = hI.resultant(EJ)
  
#             image = R(hKP*T/DeltaIJ)
    
#             hKP = prod(1/point._x-m[s] for s in K)
#             hI = kX(prod(X-m[i] for i in I))
#             DJ = kX(prod(F0(X,m[j]) for j in J))
#             DeltaIJ = hI.resultant(DJ)
#             EJ = kX(prod(F0(X,m[j])*point._x^(-2)+F1(X,m[j])*point._x^(-1)+F2(X,m[j]) for j in J))
#             T = hI.resultant(EJ)
#             image2 = R(hKP*T/DeltaIJ)
            
#             im = point._x^l*(image2)^2/(image)^2
#             return (self._codomain).lift_x(im)
            
#         else:
#             raise ValueError('Kernel has order 2.')
    
#     def domain(self):
#         return self._domain
#     def codomain(self):
#         return self._codomain
#     def kernel(self):
#         return self._kernel
#     def degree(self):
#         return self._degree

# def F0(X1,X2):
#     return (X1-X2)^2

# def F1(X1,X2,a):
#     return -2*((X1*X2+1)*(X1+X2)+2*a*X1*X2)

# def F2(X1,X2):
#     return (X1*X2-1)^2