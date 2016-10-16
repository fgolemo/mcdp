# -*- coding: utf-8 -*-
from contracts import contract
from mcdp_posets import NotBelongs, Poset, PosetProduct

from .primitive import PrimitiveDP


__all__ = [
    'Constant',
    'ConstantMinimals',
]


class Constant(PrimitiveDP):
    """ 
        A constant resource. 
        
            F = 1
            I = 1
            
    """
    
    @contract(R=Poset)
    def __init__(self, R, value):
        self.c = value

        F = PosetProduct(())
        I = PosetProduct(())
        PrimitiveDP.__init__(self, F=F, R=R, I=I)

    def evaluate(self, i):
        assert i == (), i
        fs = self.F.L(self.F.get_top())
        rs = self.R.U(self.c)
        return fs, rs
        
    def solve(self, f):
        assert f == (), f
        return self.R.U(self.c)

    def solve_r(self, r):
        F, R, c = self.F, self.R, self.c
        if R.leq(c, r):
            return F.L(()) # feasible
        else:
            return F.Ls([]) # infeasible
    
    def __repr__(self):
        return 'Constant(%s:%s)' % (self.R, self.c)


class ConstantMinimals(PrimitiveDP):
    """
        Constant antichain of resources. 
    
            F = 1
            I = 1
    """
    @contract(R=Poset)
    def __init__(self, R, values):
        """ values: set of values """ 
        F = PosetProduct(())
        I = PosetProduct(())
        self.values = values
        PrimitiveDP.__init__(self, F=F, R=R, I=I)
        self.ur = self.R.Us(self.values)

    def evaluate(self, i):
        assert i == (), i
        lf = self.F.L(self.F.get_top())
        ur = self.ur
        return lf, ur

    def solve(self, f):
        assert f == (), f
        return self.ur
    
    def solve_r(self, r):
        F = self.F
        try:
            self.ur.belongs(r)
            return F.L(()) # feasible
        except NotBelongs:
            return F.Ls([]) # infeasible
        
    def __repr__(self):
        s = len(self.values)
        return 'ConstantMins(%s:%s)' % (self.R, s)

