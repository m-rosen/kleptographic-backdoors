''' Implemnetaiton of Elligator 1 map

Written by Miriam Rosén in 2023

'''

from elligator.core import GF, legendre

# Use chi as an alias for the legendre symbol -------
chi = legendre

# Init GF --------------------------------------------
def _is_negative(self):
    """True iff self is in [p.+1 / 2.. p-1]

    An alternative definition is to just test whether self is odd.
    """
    dbl = (self.val * 2) % GF.p
    return dbl % 2 == 1

GF.is_negative = _is_negative
# ----------------------------------------------------

class Elligator1:
    def __init__(self, q, d, s):
        self.q = q
        GF.p = q
        self.d = GF(d)
        self.s = GF(s)
        self.c = GF(2) / self.s**2
        self.r = self.c + GF(1)/self.c
        self._check_theorem_1()


    def _check_theorem_1(self):
        ''' Check the properites of in theorem 1, of the Elligator paper'''
        #assert is_prime(q)
        assert self.q % 4 == 3
        
        assert self.s != GF(0)
        assert (self.s**2 - GF(2))*(self.s**2 + GF(2)) != GF(0)

        assert self.c*(self.c - GF(1))*(self.c + GF(1)) != GF(0)

        assert self.d == -(self.c + GF(1))**2 / (self.c - GF(1))**2
        assert chi(self.d) == GF(-1) # assert that d is not square
        assert self.r != GF(0)


    def map(self, t: int) -> tuple[int, int]:
        '''
        Maps the field element t to a point on the curve.
        Always succeeds.
        '''
        _t = GF(t)
        if _t == GF(1) or _t == GF(-1):
            return (GF(0), GF(1))

        u = (GF(1) - _t) / (GF(1) + _t)
        v = u**5 + (self.r**2 - GF(2))*u**3 + u
        chi_v = chi(v)
        X = chi_v*u
        Y = chi_v*v**((self.q+1) // 4)*chi_v*chi(u**2 + GF(1)/self.c**2)
        x = (self.c - GF(1))*self.s*X*(GF(1) + X)/ Y
        y = (self.r*X - (GF(1) + X)**2) / (self.r*X + (GF(1) + X)**2)

        assert x**2 + y**2 == GF(1) + self.d*x**2*y**2, "Point not on curve"
        assert u*v*X*Y*(y + GF(1)) != GF(0)
        assert Y**2 == X**5 + (self.r**2 - GF(2))*X**3 + X

        return (x.to_num(), y.to_num())


    def in_image(self, x: int, y: int) -> bool:
        ''' Check the conditions stated in theorem 3.2'''
        _x = GF(x); _y = GF(y)
        res = _y + GF(1) != GF(0)
        n = (_y - GF(1)) / (GF(2)*(_y + GF(1)))
        res &= chi((GF(1) + n*self.r)**2 - GF(1)) == GF(1)
        if n*self.r == GF(-2):
            res &= _x == 2*self.s*(self.c - GF(1))*chi(self.c)/self.r
        return res


    def inv_map(self, x: int, y: int) -> int:
        '''
        Compute the inverse map of point (x, y), returns the positive representative.
        Only defined if (x,y) is in image, otherwise returns None.
        '''
        _x = GF(x); _y = GF(y)
        if _x == GF(0) and _y == GF(1):
            return GF(1)
        
        if not self.in_image(x, y):
            return None
        
        n = (_y - GF(1)) / (GF(2)*(_y + GF(1)))
        X = -(GF(1) + n*self.r) + ((GF(1) + n*self.r)**2 - GF(1))**((self.q+1) // 4)
        z = chi((self.c - GF(1))*self.s*X*(GF(1) + X)*_x*(X**2 + GF(1)/self.c**2))
        u = z*X
        t = (GF(1) - u) / ( GF(1) + u)

        return t.abs().to_num()


def test_map(r, elli):
    '''Based on Loup Vaillant's test'''
    x, y = elli.map(r)
    p_neg = elli.map(-r)
    r_back = elli.inv_map(x, y)

    if (x, y) != p_neg : raise ValueError('+r/-r map mismatch')
    if r_back != GF(r).abs().to_num() : raise ValueError('roundtrip map mismatch')
    return (x, y)


def test_inv(x, y, elli):
    r = elli.inv_map(x, y)
    if r:
        x_back, y_back = elli.map(r)
        if x_back != x or y_back != y:
            raise ValueError('roundtrip mismatch (rev_map)')
    return r


if __name__ == "__main__":
    import random
    # Test with Hemmert's curve
    q = 2**257 - 93
    d = 1088
    s = 14697352851676074552963121469662559050531125212681422018744685276304061464803
    elli = Elligator1(q, d, s)
    
    for i in range(0, 100):
        r = random.randint(0, q - 1)
        test_map(r, elli)

