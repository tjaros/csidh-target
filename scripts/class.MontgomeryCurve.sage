class MontgomeryCurve(object):
    def __init__(self,field, coef):
        self._field = field
        self._coef = coef
        self._prime = field.characteristic()
        self._size = field.characteristic()^field.degree()
        self._discriminant = self._coef^2 - 4
    def __repr__(self):
        s = "Montgomery elliptic curve defined by y^2 = x^3 + "
        if (self._coef == 0):
            s += "x"
        else:
            s += "%s*x^2 + x "%self._coef
        if (self._field.degree() == 1):
            s += " over finite field of size %s."%self._prime
        else:
            s += " over finite field of size %s^%s."%(self._prime,self._field.degree())
        return s
    def __eq__(self, other):
        return (self._field, self._coef) == (other._field, other._coef)
    def __call__(self, *arg,**kwarg):
        R = self._field
        if (len(arg) == 1):
            if arg[0] == 0:
                return PointMC(R(0),R(1),R(0), self)
            else:
                return PointMC(R(arg[0]), R(self.lift_x(arg[0]).y()), 1, self)
    def coef(self):
        return self._coef
    def field(self):
        return self._field
    def j_invariant(self):
        R = self._field
        return R(256*((self._coef)^2 - 3)^3/((self._coef)^2-4))
    def discriminant(self):
        return self._discriminant
 
 ###################################################
###################################################
###################################################  


    #function
    def is_Mont_EC(self):
        if (self._discriminant == 0):
            return False
        else:
            return True
 ###################################################
###################################################
###################################################   


    def is_supersingular(self, primes_list):
        '''
        Algorithm to key validation from https://csidh.isogeny.org/csidh-20181118.pdf
        '''
        R = self._field
        val = False
        if (primes_list != [3,5]):
            while not (val):
                d = 1
                point = self.random_point(MF = True)
                for l in primes_list:
                    k = R((self._prime + 1) / l)
                    Q = point.mLadder(k)
                    if not (Q.mLadder(l) == self(0).transformMF()):
                        return False
                        break                
                    if not (Q == self(0).transformMF()):
                        d = l * d
                    if (d > 4*sqrt(self._prime)): #this never happend when primes_list = [3,5]
                        return True
                        break
        else:
            raise ValueError("We can't use this algorithm")
            
 ###################################################
###################################################
###################################################   

    def is_x_coord(self, x):
        '''
        Is point with x-corrd x on self?
        '''
        R = self._field
        if (R(x^3 + self._coef * x^2 + x).is_square()):
            return True
        else:
            return False
 
 ###################################################
###################################################
###################################################  

    def is_point(self, point):
        '''
        Is point on self?
        '''
        R = self._field
        x = point._x
        y = point._y
        A = self._coef
        point = point.transformZ()
        if self.is_x_coord(x):
            return R(x^3 + A * x^2 + x).sqrt() == y or R(x^3 + A * x^2 + x).sqrt() == -y
        else:
            return False

         ###################################################
###################################################
###################################################  

    def twist(self):
        '''
        Return twist Et.
        '''
        R = self._field
        return MontgomeryCurve(self._field, R(-self._coef))
 ###################################################
###################################################
###################################################  
    
    
    def points_x(self):
        '''
        All points on E.
        '''
        R = self._field
        points = [R(x) for x in range(0, self._prime) if self.is_x_coord(x)]
        #print(points)
        return points

 ###################################################
###################################################
###################################################      
    
    def lift_x(self, x, MF = False, all = False):
        '''
        Construct point with x-coordinate x on self.
        '''
        if not self.is_x_coord(x):
            raise ValueError("No point with x. %s on this curve"%x)
        else:
            R = self._field
            if (MF == True):
                return PointMC(R(x), None, 1, self)
            else: 
                y = R(x^3 + self._coef * x^2 + x).sqrt()
                if (all == False):        
                    return PointMC( R(x), R(y), 1, self)
                else:
                    return PointMC(R(x), R(y), 1, self), PointMC(R(x), R(-y), 1, self)
 
 ###################################################
###################################################
###################################################  

    def random_point(self, MF = False):
        r"""
        This algorithm generates random point on some elliptic curve, 
        this point has order different from 2 (and 1). 
        There is a lot of algorithms that want this point to have order different from 2.
        """
        R = self._field
        help1 = False
        x = ZZ.random_element(self._prime - 1) + 1
        while not (self.is_x_coord(x)):
                x = ZZ.random_element(self._prime - 1) + 1
        if (MF == False):
            return self.lift_x(x, MF = False, all = False)
        else:
            return self.lift_x(x, MF = True, all = False)

 ###################################################
###################################################
###################################################          
        
    def transformM2TE(self):
        R = self._field
        return EdwardCurve(R,R(self._coef - 2), R(self._coef + 2))
    
        R = self._field
        if ((R(self._coef - 2)).is_square()):
            d = R((self._coef + 2)/(self._coef - 2))
        else:
            d = R((self._coef - 2)/(self._coef + 2))
        return EdwardCurve(R,d, 1) 
    
 ###################################################
###################################################
###################################################  

    def isogenyMF(self, point, l):
        r"""
This algorithm computes the coef of E': y2 = x3 + Bx2 + x, which is l-isogenous with E: y2 = x3 + Ax2 + x
#formula B = PI(A - 3*SI), where PI is product of x-coord. of all points in <K> (except onfinity), and SI is sum over all points in <K> (except infinity) of (x-coord - 1/x-coord.)    


        """
        R = self._field
        PI = R(point._x)
        SI = R(point._x - 1/point._x)
        for i in range(2,l):
            point1 = point.mLadder(i)
            PI = PI * point1._x 
            SI = SI + R(point1._x - (1/point1._x))
        codomain = MontgomeryCurve(R,R(PI*(self._coef - 3*SI)))
        return IsogenyMC(domain = self, codomain = codomain, kernel = point, baseDegree = l)
        """
        not point of order 2
        i = 1
        m = 0
        while (i < l):
            KK = i*K
            if ((KK[0] == 0) & (KK[1] == 0)):
                m = 1
                break
            i = i+1
        if (m == 1):
            print('There is  point with order 2')
        return B   
        """
 ###################################################
###################################################
###################################################          
        
        
    def isogenyEF(self, point, l):
        r"""
This functions compute coef B of E', which is l-isogeny to self, using arithmetic on Edward curves.
https://eprint.iacr.org/2019/843.pdf
        """
        R = self._field
        a = self._coef + 2 #tranformation from MF to EF
        d = self._coef - 2
        M = 1
        N = 1
        s = (l - 1)//2
        for i in range(1, s + 1):
            point1 = point.mLadder(i)
            Y = (point1._x - point1._z)
            T = (point1._x + point1._z)
            M = R(M*Y)
            N = R(N*T)
            
        aNew = R((a^l)*(N^8))
        dNew = R((d^l)*(M^8))
        
        return IsogenyMC(domain = self, codomain = MontgomeryCurve(R, R(2*(aNew + dNew)/(aNew - dNew))), kernel = point, baseDegree = l)

 ###################################################
###################################################
###################################################      
    
    def isogenyEF2(self, point, l):
        r"""
This functions compute coef B of E', which is l-isogeny to self, using arithmetic on Edward curves.
        """
        R = self._field
        #tranformation from MF to EF
        if ((R(self._coef - 2)).is_square()):
            d = R((self._coef + 2)/(self._coef - 2))
        else:
            d = R((self._coef - 2)/(self._coef + 2))
        M = 1
        N = 1
        s = (l - 1)//2
        for i in range(1, s + 1):
            point1 = point.mLadder(i)
            Y = (point1._x - point1._z)
            T = (point1._x + point1._z)
            M = R(M*Y)
            N = R(N*T)
            
        aNew = R((N^8))
        dNew = R((d^l)*(M^8))
        
        return IsogenyMC(domain = self, codomain = MontgomeryCurve(R, R(2*(aNew + dNew)/(aNew - dNew))), kernel = point, baseDegree = l)

 ###################################################
###################################################
###################################################      
    
    def isogeny_sqrt(self, kernel, l, m):
        r"""
This algorithm computes the coef of E': y2 = x3 + Bx2 + x, which is l-isogenous with E: y2 = x3 + Ax2 + x

Using Velu-sqrt,  m = {s: kernel.mLadder(s)._x for s in S} is  precomputed   

https://velusqrt.isogeny.org/velusqrt-20200616.pdf
        """
        
        R = self._field
        A = R(self._coef)
        kX.<X> = R[]

        S = set(range(1,l-1,2))
        hS = kX(prod(X-m[s] for s in S))
        r = R(hS(1)/hS(-1))
#         r = prod((m[s]-1)/(m[s]+1) for s in S)
        d = R(((A-2)/(A+2))^l * r^8 )
        coef1 = R(2*(1+d)/(1-d))
        return IsogenyMC_sqrt(domain = self, codomain = MontgomeryCurve(R,coef1), kernel = kernel, baseDegree = l, exponent = 1)

     ###################################################
###################################################
###################################################  


    def isogeny_sqrt2(self, kernel, l):
        r"""
This algorithm computes the coef of E': y2 = x3 + Bx2 + x, which is l-isogenous with E: y2 = x3 + Ax2 + x

Using Velu-sqrt,  m = {s: kernel.mLadder(s)._x for s in S} is NOT precomputed   

https://velusqrt.isogeny.org/velusqrt-20200616.pdf
        """
        
        R = self._field
        A = R(self._coef)
        kX.<X> = R[]

        S = set(range(1,l-1,2))

        m = {s: kernel.mLadder(s)._x for s in S}
        hS = kX(prod(X-m[s] for s in S))
        r = R(hS(1)/hS(-1))
#         r = prod((m[s]-1)/(m[s]+1) for s in S)
        d = R(((A-2)/(A+2))^l * r^8 )
        coef1 = R(2*(1+d)/(1-d))
        return IsogenyMC_sqrt(domain = self, codomain = MontgomeryCurve(R,coef1), kernel = kernel, baseDegree = l, exponent = 1)
 
 ###################################################
###################################################
###################################################  
    def pushPointW2M(self,curveW, pointW):
        r"""
We have got some Montgomery curve (coef A), which is isomorphic to elliptic curve in SW form (curveW). For any point pointW on curveW we can find corresponding point on self.   

Input: curveW... EC in SW form
       pointW... point on curveW
Output: corresponding point on Montgomery curve (self)
        """
        m = 1
        alpha = findAlpha(curveW,self._field,self._prime)
        S = (sqrt(3*alpha^2 + curveW.a4()))^(-1)
        if(kronecker(S,p)==-1):
            m = -1
        x = m*S*(pointW[0] - alpha)
        for i in range(1,self._prime):
            if (Mod(i^2, self._prime) == m*S):
                break
        y = pointW[1]*S*i
        return PointMC(x, y, 1, self)
 ###################################################
###################################################
###################################################      


    def findIndices(self,key, sign):
        S = []
        for i in range(len(key)):
            if key[i] != 0 and key[i] * sign > 0:
                S.append(i)
        return S
            
    def classGroupEvaluation(self, key, primes_list):
        r"""
        Fuction made for CSIDH algorithm.

        Algorithm to evaluate class group (composition of isogeny of order li's)
        Input: T is a2 coef of E (domain)
               key is private key
               primes_list is list of small primes numbers, defining degree of isogenies
        Output: curve ER (result of class group action)
        """
        F = self._field
        ER = self
        while not(key == [0]*len(primes_list)):
            ST = self.findIndices(key,1) #set S for T --- ST
            SmT = self.findIndices(key,-1) #set S for -T --- SmT
            [ER, key] = ER.oneStepIsogeny(ST,1,key,primes_list)
            [ER, key] = ER.oneStepIsogeny(SmT,-1,key,primes_list)
        return ER
    
  ###################################################
###################################################
###################################################   

    def oneStepIsogeny(self,ST, s,key, primes_list):
        r"""
        Fuction made for CSIDH algorithm.

        This function takes private key and computes one step of each li-isogeny according this key.

        Input: ST... list of indices with sign = s
               s... -1 twist, 1 curve
               key... private key
               primes_list... list of primes
               prime... prime p, field Fp
        Output: ET... codomain of this sequence of li-isogenies
                T... coef of ET
                key... edited key 
        """
        T = self._coef
        F = self._field
        p = self._prime
        if not(ST== []): # ST = [] means, that we have made all steps in this direction
            ET = MontgomeryCurve(F,s*T) #elliptic curve with a2=T, if s=-1, we have to move on twist
            xt = ET.random_point(MF = True) #take random point
            k = product([primes_list[i] for i in ST])
            
            l = (p+1)//k
            Q = xt.mLadder(l)#computing Q
            for i in ST:
                m=k//primes_list[i]
                R = Q.mLadder(m) #compute point with order li (=primes_list[i])
                if not(R == ET(0)): #codomain
                    phi = ET.isogenyEF(R, primes_list[i])
                    ET = phi.codomain()
                    Q = phi(Q)
                    k=m
                    key[i]=key[i]-s
                    T = phi.codomain().coef()*s  
        ET = MontgomeryCurve(F,T) #elliptic curve with a2=T
        return ET,key
    
    
    
