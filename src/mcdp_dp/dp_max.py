# -*- coding: utf-8 -*-
from .dp_flatten import Mux
from .dp_generic_unary import WrapAMap
from .primitive import PrimitiveDP
from contracts import contract
from mcdp_posets import Map, Poset, PosetProduct, SpaceProduct
# from mocdp import get_conftools_posets


__all__ = [
    'Max',
    'Max1',
    'Min',
    'JoinNDP',
]

class Max(PrimitiveDP):
    """ Join on a poset """

    def __init__(self, F0):
#         library = get_conftools_posets()
#         _, F0 = library.instance_smarter(F)

        F = PosetProduct((F0, F0))
        R = F0
        self.F0 = F0

        M = SpaceProduct(())
        PrimitiveDP.__init__(self, F=F, R=R, M=M)

    def solve(self, func):
        f1, f2 = func

        # F = self.get_fun_space()
        r = self.F.join(f1, f2)

        return self.R.U(r)

    def __repr__(self):
        return 'Max(%r)' % self.F0


class Max1Map(Map):
    def __init__(self, F, value):
        Map.__init__(self, F, F)
        self.value = value
        self.F = F
        self.F.belongs(value)
        
    def _call(self, x):
        # self.F.belongs(x)
        r = self.F.join(x, self.value)
        return r
        

class Max1(WrapAMap):

    def __init__(self, F, value):
        assert isinstance(F, Poset)
        m = Max1Map(F, value)
        WrapAMap.__init__(self, m)
        self.value = value

    def __repr__(self):
        return 'Max1(%r, %s)' % (self.F, self.value)

class Min(PrimitiveDP):
    """ Meet on a poset """

    def __init__(self, F):  #
        assert isinstance(F, Poset)
        FF = PosetProduct((F, F))
        R = F
        self.F0 = F

        M = SpaceProduct(())
        PrimitiveDP.__init__(self, F=FF, R=R, M=M)

    def solve(self, func):
        f1, f2 = func

        r = self.F0.meet(f1, f2)

        return self.R.U(r)

    def __repr__(self):
        return 'Min(%r)' % self.F0

class JoinN(Map):
    """ A map that joins n arguments. """

    @contract(n='int,>=1', P=Poset)
    def __init__(self, n, P):
        dom = PosetProduct((P,) * n)
        cod = P
        Map.__init__(self, dom, cod)
        self.P = P

    def _call(self, xs):
        res = xs[0]
        for x in xs[1:]:
            res = self.P.join(res, x)
        return res
    
class JoinNDP(WrapAMap):
    def __init__(self, n, P):
        amap = JoinN(n, P)
        WrapAMap.__init__(self, amap)

class MeetNDual(Mux):
    """ This is just a Mux """
    def __init__(self, n, P):
        coords = [()] * n
        Mux.__init__(self, P, coords)

        
        
        
        
