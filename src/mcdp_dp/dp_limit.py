# -*- coding: utf-8 -*-
from contracts import contract
from mcdp_dp.primitive import NotFeasible
from mcdp_posets import (LowerSet, NotBelongs, Poset, PosetProduct, UpperSet,
                         LowerSets)
from mocdp.exceptions import do_extra_checks, mcdp_dev_warning

from .primitive import PrimitiveDP


_ = Poset

__all__ = [
    'Limit',
    'LimitMaximals',
    'FuncNotMoreThan',
]

class FuncNotMoreThan(PrimitiveDP):
    """
        Checks that f ≼ limit
        
        f ⟼   {f},  if f ≼ limit
                ø,    otherwise
        
        h* : r  ⟼ {r} 
                
    """
    @contract(F='$Poset')
    def __init__(self, F, limit):
        F.belongs(limit)
        self.limit = limit
        R = F
        I = F
        PrimitiveDP.__init__(self, F=F, R=R, I=I)

    def evaluate(self, i):
        mcdp_dev_warning('what should we do if it is not feasible?')
        if self.F.leq(i, self.limit):
            rs = self.R.U(i)
            fs = self.F.L(i)
        else:
            rs = self.R.Us(set([]))
            fs = self.F.Ls(set([]))
        return fs, rs

    def get_implementations_f_r(self, f, r):
        if self.F.leq(f, r) and self.F.leq(f, self.limit):
            return set([f])
        else:
            raise NotFeasible()
        
    def solve(self, f):
        if self.F.leq(f, self.limit):
            return self.R.U(f)
        else:
            empty = self.R.Us(set())
            return empty
        
    def solve_r(self, r):  # @UnusedVariable
        mcdp_dev_warning('think more about this')
        return self.F.L(self.limit)
        
    def __repr__(self):
        return 'FuncNotMoreThan(%s)' % (self.F.format(self.limit))

    def repr_h_map(self):
        return 'f ⟼ f if f ≼ %s, else ø' % self.F.format(self.limit)

    def repr_hd_map(self):
        return 'r ⟼ {%s}' % self.F.format(self.limit)


class Limit(PrimitiveDP):
    """
        Checks that f ≼ value
        
        f ⟼   {⟨⟩},  if f ≼ value
                ø,    otherwise
        
        h* : ⟨⟩  ⟼ {value}
                
    """
    @contract(F='$Poset')
    def __init__(self, F, value):
        F.belongs(value)
        self.limit = value

        R = PosetProduct(())
        I = PosetProduct(())
        PrimitiveDP.__init__(self, F=F, R=R, I=I)

    def evaluate(self, i):
        assert i == ()
        rs = self.R.U(self.R.get_bottom())
        fs = self.F.L(self.limit)
        return fs, rs

    def solve(self, f):
        if self.F.leq(f, self.limit):
            res = self.R.U(())
            return res
        else:
            empty = self.R.Us(set())
            return empty
        
    def solve_r(self, r):
        assert r == ()
        return self.F.L(self.limit)
        
    def __repr__(self):
        return 'Limit(%s, %s)' % (self.F, self.F.format(self.limit))

    def repr_h_map(self):
        return 'f ⟼ {⟨⟩} if f ≼ %s, else ø' % self.F.format(self.limit)

    def repr_hd_map(self):
        return '⟨⟩ ⟼ {%s}' % self.F.format(self.limit)


class LimitMaximals(PrimitiveDP):

    """
        
        h: f ⟼ {⟨⟩},  if f \in \downarrow values
                ø,    otherwise
        
        h* : ⟨⟩  ⟼ values
                
    """
    
    @contract(F='$Poset', values='seq|set')
    def __init__(self, F, values):
        if do_extra_checks():
            for value in values:
                F.belongs(value)

        self.limit = LowerSet(values, F)

        R = PosetProduct(())
        M = PosetProduct(())
        PrimitiveDP.__init__(self, F=F, R=R, I=M)

    def evaluate(self, m):
        assert m == ()
        lf = self.limit
        ur = UpperSet(set([()]), self.R)
        return lf, ur
        
    def solve(self, f):
        try:
            # check that it belongs
            self.limit.belongs(f)
        except NotBelongs:
            empty = UpperSet(set(), self.R)
            return empty
        res = UpperSet(set([()]), self.R)
        return res

    def solve_r(self, r):
        assert r == ()
        return self.limit
    
    def __repr__(self):
        s = len(self.limit.maximals)
        return 'LimitMaximals(%s, %s els)' % (self.F, s)
    
    def repr_h_map(self):
        LF = LowerSets(self.F)
        return 'f ⟼ {⟨⟩} if f ∈ %s, else ø' % LF.format(self.limit)

    def repr_hd_map(self):
        contents = ", ".join(self.F.format(m)
                for m in sorted(self.limit.maximals))
        return '⟨⟩ ⟼ {%s}' % contents

