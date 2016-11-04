# -*- coding: utf-8 -*-
from contracts import contract
from contracts.utils import raise_desc, check_isinstance
from mcdp_maps.repr_map import repr_map_product
from mcdp_posets import Nat, Poset, PosetProduct, is_top
from mcdp_posets.nat import Nat_mult_lowersets_continuous
from mcdp_posets.rcomp import Rcomp_multiply_upper_topology_seq
from mocdp.exceptions import mcdp_dev_warning

from .primitive import ApproximableDP, NotSolvableNeedsApprox, PrimitiveDP
from .repr_strings import repr_h_map_invmult
from .sequences_invplus import Nat_mult_antichain_Min, invmultL_solve_options, invmultU_solve_options


_ = Nat, Poset

__all__ = [
    'InvMult2',
    'InvMult2U',
    'InvMult2L',
    'InvMult2Nat',
]
 

class InvMult2(ApproximableDP):

    ALGO_UNIFORM = 'uniform'
    ALGO_VAN_DER_CORPUT = 'van_der_corput'
    ALGO = ALGO_VAN_DER_CORPUT

    @contract(Rs='tuple[2],seq[2]($Poset)')
    def __init__(self, F, Rs):
        R = PosetProduct(Rs)
        self.F = F
        self.Rs = Rs
        M = PosetProduct((F, R))
        PrimitiveDP.__init__(self, F=F, R=R, I=M)

    def evaluate(self, m):
        raise NotSolvableNeedsApprox(type(self))

    def solve(self, f):
        raise NotSolvableNeedsApprox(type(self))
    
    def solve_r(self, r):
        mcdp_dev_warning('this is not coherent with solve()')
        fmax = Rcomp_multiply_upper_topology_seq(self.Rs, r, self.F)
        return self.F.L(fmax)
    
    def repr_h_map(self):
        return repr_h_map_invmult(len(self.Rs))
    
    def repr_hd_map(self):
        return repr_map_product('r', len(self.Rs))    

    def get_lower_bound(self, n):
        return InvMult2L(self.F, self.Rs, n)

    def get_upper_bound(self, n):
        return InvMult2U(self.F, self.Rs, n)

    def __repr__(self):
        return 'InvMult2(%s → %s)' % (self.F, self.R)


class InvMult2U(PrimitiveDP):

    @contract(Rs='tuple[2],seq[2]($Poset)')
    def __init__(self, F, Rs, n):
        R = PosetProduct(Rs)

        M = PosetProduct((F, R))
        self.F = F
        self.Rs = Rs
        self.R = R
        PrimitiveDP.__init__(self, F=F, R=R, I=M)

        self.n = n

    def evaluate(self, m):
        f, r = m
        ur = self.R.U(r)
        lf = self.F.L(f)
        return lf, ur

    def get_implementations_f_r(self, f, r):  # @UnusedVariable
        # TODO: check feasible
        return set([(f, r)])

    def solve(self, f):
        algo = InvMult2.ALGO
        options = invmultU_solve_options(F=self.F, R=self.R, f=f, n=self.n, algo=algo)
        return self.R.Us(options)
    
    def solve_r(self, r):
        mcdp_dev_warning('this is not coherent with solve()')
        fmax =  Rcomp_multiply_upper_topology_seq(self.Rs, r, self.F)
        return self.F.L(fmax)

    def repr_h_map(self):
        return repr_h_map_invmult(len(self.Rs))
    
    def repr_hd_map(self):
        return repr_map_product('r', len(self.Rs)) + ' (approx)'


class InvMult2L(PrimitiveDP):

    @contract(Rs='tuple[2],seq[2]($Poset)')
    def __init__(self, F, Rs, n):
        R = PosetProduct(Rs)
        M = PosetProduct((F, R))
        self.F = F
        self.Rs = Rs

        PrimitiveDP.__init__(self, F=F, R=R, I=M)
        self.R = R
        self.n = n

    def get_implementations_f_r(self, f, r):  # @UnusedVariable
        mcdp_dev_warning('TODO: check feasible')
        return set([(f, r)])

    def evaluate(self, m):
        f, r = m
        ur = self.R.U(r)
        lf = self.F.L(f)
        return lf, ur

    def solve_r(self, r):
        mcdp_dev_warning('This might not be correct')
        fmax = Rcomp_multiply_upper_topology_seq(self.Rs, r, self.F)
        return self.F.L(fmax)
    
    def solve(self, f):
        algo = InvMult2.ALGO
        options = invmultL_solve_options(F=self.F, R=self.R, f=f, n=self.n, algo=algo)
        return self.R.Us(options)
        
    def repr_h_map(self):
        return repr_h_map_invmult(len(self.Rs))
    
    def repr_hd_map(self):
        return repr_map_product('r', len(self.Rs)) + ' (approx)'    

class InvMult2Nat(ApproximableDP):
    """
        Implements:
        
             f ≤ r₁ * r₂
        
        with f,r₁,r₂ ∈ ℕ.
        
    """
    memory_limit = 10000
    
    @contract(Rs='tuple[2],seq[2]($Nat)', F=Nat)
    def __init__(self, F, Rs):
        if not len(Rs) == 2:
            raise ValueError(Rs)
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
        if is_top(self.F, f):
            top = f
            elements = set([(top, 1), (1, top)]) # XXX: to check
            return self.R.Us(elements) 
        
        if f > InvMult2Nat.memory_limit:
            msg = ('InvMult2Nat:solve(%s): This would produce' 
                   ' an antichain of length %s.') % (f,f)
            raise NotSolvableNeedsApprox(msg)
            
        options = Nat_mult_antichain_Min(f)
        return self.R.Us(options)
    
    def get_lower_bound(self, n):  # @UnusedVariable
        msg = 'InvMult2Nat:get_lower_bound() not implemented yet'
        raise_desc(NotImplementedError, msg)
    
    def get_upper_bound(self, n):  # @UnusedVariable
        msg = 'InvMult2Nat:get_upper_bound() not implemented yet'
        raise_desc(NotImplementedError, msg)
        
    def solve_r(self, r):
        r1, r2 = r
        f_max = Nat_mult_lowersets_continuous(r1, r2)
        return self.F.L(f_max)

    def get_implementations_f_r(self, f, r):
        return set([(f, r)])

    def __repr__(self):
        return 'InvMult2Nat(%s -> %s)' % (self.F, self.R)
    
    def repr_h_map(self):
        return repr_h_map_invmult(len(self.R))
    
    def repr_hd_map(self):
        return repr_map_product('r', len(self.R))

    