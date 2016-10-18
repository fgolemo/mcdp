# -*- coding: utf-8 -*-
from contracts import contract
from contracts.utils import check_isinstance
from mcdp_posets import Nat, PosetProduct
from mcdp_posets.nat import Nat_add
from mcdp_posets.poset import is_top

from .primitive import PrimitiveDP


__all__ = [
    'InvPlus2Nat',
]

class InvPlus2Nat(PrimitiveDP):
    """
        Implements:
        
             f <= r₁ + r₂
        
        with f,r₁,r₂ ∈ ℕ.
        
    """
    @contract(Rs='tuple[2],seq[2]($Nat)', F=Nat)
    def __init__(self, F, Rs):
        for _ in Rs:
            check_isinstance(_, Nat)
        check_isinstance(F, Nat)
        R = PosetProduct(Rs)
        M = PosetProduct((F, R))
        PrimitiveDP.__init__(self, F=F, R=R, I=M)

    def evaluate(self, m):
        f, r = m
        ur = self.R.U(r)
        lf = self.F.L(f)
        return lf, ur

    def solve(self, f):
        # FIXME: what about the top?
        top = self.F.get_top()
        if is_top(self.F, f):
            s = set([(top, 0), (0, top)])
            return self.R.Us(s)

        assert isinstance(f, int)

        s = set()
        for o in range(f + 1):
            s.add((o, f - o))

        return self.R.Us(s)
    
    def solve_r(self, r):
        r1, r2 = r
        f = Nat_add(r1, r2)
        return self.F.L(f)

    def get_implementations_f_r(self, f, r):
        return set([(f, r)])

    def __repr__(self):
        return 'InvPlus2Nat(%s -> %s)' % (self.F, self.R)

