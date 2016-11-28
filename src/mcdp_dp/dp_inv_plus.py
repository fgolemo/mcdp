# -*- coding: utf-8 -*-
from contracts import contract
from contracts.utils import check_isinstance, raise_desc
from mcdp_posets import Nat, Poset, PosetProduct, RcompUnits
from mcdp_posets import Rcomp, get_types_universe, is_top
from mcdp_posets.nat import Nat_add
from mocdp.exceptions import DPInternalError, mcdp_dev_warning

from .primitive import ApproximableDP, NotSolvableNeedsApprox, PrimitiveDP
from .repr_strings import invplus2_repr_h_map, invplus2_repr_hd_map
from .sequences_invplus import sample_sum_lowerbound, sample_sum_upperbound


_ = Nat, Poset

__all__ = [
    'InvPlus2',
    'InvPlus2U',
    'InvPlus2L',
    'InvPlus2Nat',
]

mcdp_dev_warning('FIXME: bug - are we taking into account the units?')

class InvPlus2(ApproximableDP):
    ALGO_UNIFORM = 'uniform'
    ALGO_VAN_DER_CORPUT = 'van_der_corput'
    ALGO = ALGO_VAN_DER_CORPUT

    @contract(Rs='tuple[2],seq[2]($RcompUnits|$Rcomp)', F='$RcompUnits|$Rcomp')
    def __init__(self, F, Rs):
        for _ in Rs:
            check_isinstance(_, (Rcomp, RcompUnits))
        check_isinstance(F, (Rcomp, RcompUnits))
        self.Rs = Rs
        R = PosetProduct(Rs)

        tu = get_types_universe()
        if not tu.equal(Rs[0], Rs[1]) or not tu.equal(F, Rs[0]):
            msg = 'InvPlus only available for consistent units.'
            raise_desc(DPInternalError, msg, F=F, Rs=Rs)

        M = PosetProduct((F, R))
        PrimitiveDP.__init__(self, F=F, R=R, I=M)

    def solve(self, f):
        raise NotSolvableNeedsApprox(type(self))

    def solve_r(self, r):
        r1, r2 = r
        maxf = self.F.add(r1, r2)
        return self.F.L(maxf)

    def evaluate(self, m):
        raise NotSolvableNeedsApprox(type(self))

    @contract(n='int,>=0')
    def get_lower_bound(self, n):
        F = self.F
        Rs = self.Rs
        dp = InvPlus2L(F, Rs, n) 
        return dp

    @contract(n='int,>=0')
    def get_upper_bound(self, n):
        F = self.F
        Rs = self.Rs
        dp = InvPlus2U(F, Rs, n) 
        return dp

    def get_implementations_f_r(self, f, r):  # @UnusedVariable
        raise NotSolvableNeedsApprox(type(self))

    def repr_h_map(self):
        return invplus2_repr_h_map('f', 'r')

    def repr_hd_map(self):
        return invplus2_repr_hd_map('r')
    

class InvPlus2L(PrimitiveDP):
    """ 
        Lower approximation to f <= r1 + r2 on R.
    """

    @contract(Rs='tuple[2],seq[2]($RcompUnits|$Rcomp)', F='$RcompUnits|$Rcomp')
    def __init__(self, F, Rs, nl):
        for _ in Rs:
            check_isinstance(_, (Rcomp, RcompUnits))
        check_isinstance(F, (Rcomp, RcompUnits))
        R = PosetProduct(Rs)
        M = PosetProduct((F, R))
        PrimitiveDP.__init__(self, F=F, R=R, I=M)
        self.nl = nl

    def evaluate(self, m):
        f, r = m
        ur = self.R.U(r)
        lf = self.F.L(f)
        return lf, ur

    def get_implementations_f_r(self, f, r):  # @UnusedVariable
        return set([(f, r)])

    def solve(self, f):
        options = sample_sum_lowerbound(self.F, self.R, f, self.nl)
        return self.R.Us(options)
    
    def solve_r(self, r):
        """ 
            Upper approximation to f <= r1 + r2 on R.
        """
        r1, r2 = r
        maxf = self.F.add(r1, r2)
        return self.F.L(maxf)
    
    def repr_h_map(self):
        return invplus2_repr_h_map('f', 'r') + ' (approx)'

    def repr_hd_map(self):
        return invplus2_repr_hd_map('r')

    

class InvPlus2U(PrimitiveDP):

    @contract(Rs='tuple[2],seq[2]($RcompUnits|$Rcomp)', F='$RcompUnits|$Rcomp')
    def __init__(self, F, Rs, nu):
        for _ in Rs:
            check_isinstance(_, (Rcomp, RcompUnits))
        check_isinstance(F, (Rcomp, RcompUnits))

        R = PosetProduct(Rs)
        M = PosetProduct((F, R))
        PrimitiveDP.__init__(self, F=F, R=R, I=M)
        self.nu = nu

    def get_implementations_f_r(self, f, r):  # @UnusedVariable
        return set([(f, r)])

    def evaluate(self, m):
        f, r = m
        ur = self.R.U(r)
        lf = self.F.L(f)
        return lf, ur

    def solve(self, f):
        #print('InvPlus2.ALGO : ', InvPlus2.ALGO )
        options = sample_sum_upperbound(self.F, self.R, f, self.nu)
        return self.R.Us(options)

    def solve_r(self, r):
        r1, r2 = r
        maxf = self.F.add(r1, r2)
        return self.F.L(maxf)
    
    def repr_h_map(self):
        return invplus2_repr_h_map('f', 'r') + ' (approx)'

    def repr_hd_map(self):
        return invplus2_repr_hd_map('r')


class InvPlus2Nat(PrimitiveDP):
    """
        Implements:
        
             f ≤ r₁ + r₂
        
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
        
        if f >= 100000:
            msg = 'This would create an antichain of %s items.' % f
            raise NotSolvableNeedsApprox(msg)
        
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

    def repr_h_map(self):
        return invplus2_repr_h_map('f', 'r')

    def repr_hd_map(self):
        return invplus2_repr_hd_map('r')

