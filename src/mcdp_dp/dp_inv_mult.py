# -*- coding: utf-8 -*-
from contracts import contract
from contracts.utils import raise_desc, check_isinstance
from mcdp_posets import Nat, Poset, PosetProduct, is_top
from mcdp_posets.nat import Nat_mult_lowersets_continuous
from mcdp_posets.rcomp import Rcomp_multiply_upper_topology_seq
from mcdp_posets.utils import check_minimal
from mocdp.exceptions import do_extra_checks, mcdp_dev_warning
import numpy as np

from .primitive import ApproximableDP, NotSolvableNeedsApprox, PrimitiveDP


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


def invmultU_solve_options(F, R, f, n, algo):
    """ Returns a set of points in R that are on the line r1*r2=f. """
    assert algo in [InvMult2.ALGO_UNIFORM, InvMult2.ALGO_VAN_DER_CORPUT]
    if is_top(F, f):
        mcdp_dev_warning('FIXME Need much more thought about this')
        top1 = R[0].get_top()
        top2 = R[1].get_top()
        s = set([(top1, top2)])
        return s

    check_isinstance(f, float)
            
    if f == 0.0:
        return set([(0.0, 0.0)])

    if algo == InvMult2.ALGO_UNIFORM:
        mcdp_dev_warning('TODO: add ALGO as parameter. ')
        ps = samplec(n, f)
    elif algo == InvMult2.ALGO_VAN_DER_CORPUT:
        x1, x2 = generate_exp_van_der_corput_sequence(n=n, C=f)
        ps = zip(x1, x2)
    else: # pragma: no cover
        assert False
    return ps

def invmultL_solve_options(F, R, f, n, algo):
    """ Returns a set of points that are *below* r1*r2 = f """
    assert algo in [InvMult2.ALGO_UNIFORM, InvMult2.ALGO_VAN_DER_CORPUT]
    
    if f == 0.0:
        return set([(0.0, 0.0)])

    top = F.get_top()
    if f == top:
        mcdp_dev_warning('FIXME Need much more thought about this')
        top1 = R[0].get_top()
        top2 = R[1].get_top()
        s = set([(top1, 0.0), (0.0, top2)])
        return s

    if algo == InvMult2.ALGO_UNIFORM:
        if n == 1:
            points = [(0.0, 0.0)]
        elif n == 2:
            points = [(0.0, 0.0)]
        else:
            pu = sorted(samplec(n - 1, f), key=lambda _: _[0])
            assert len(pu) == n - 1, (len(pu), n - 1)
            nu = len(pu)

            points = set()
            points.add((0.0, pu[0][1]))
            points.add((pu[-1][0], 0.0))
            for i in range(nu - 1):
                p = (pu[i][0], pu[i + 1][1])
                points.add(p)

    elif algo == InvMult2.ALGO_VAN_DER_CORPUT:

        if n == 1:
            points = set([(0.0, 0.0)])
        else:
            x1, x2 = generate_exp_van_der_corput_sequence(n=n - 1, C=f)
            pu = zip(x1, x2)
            assert len(pu) == n - 1, pu

            if do_extra_checks():
                check_minimal(pu, R)

            nu = len(pu)
            points = []
            points.append((0.0, pu[0][1]))

            for i in range(nu - 1):
                p = (pu[i][0], pu[i + 1][1])
                points.append(p)

            points.append((pu[-1][0], 0.0))

            points = set(points)
    else: # pragma: no cover
        assert False

    assert len(points) == n, (n, len(points), points)

    return points

def samplec(n, c):
    """ Samples n points on the curve xy=c """
    ps = sample(n)
    assert len(ps) == n, (n, len(ps), ps)
    s = np.sqrt(c)
    ps = [(x * s, y * s) for x, y in ps]
    return ps

@contract(n='int,>=1', returns='list(tuple(float, float))')
def sample(n):
    """ Samples n points on the curve xy=1 """
    assert n >= 1
    points = set()

    # divide the interval [0,1] equally in n/2 intervals
    m = n / 2
    xs = np.linspace(0.0, 1.0, m + 2)[1:-1]
    ys = 1.0 / xs
    if m * 2 < n:  # odd
        points.add((1.0, 1.0))
    points.update(zip(xs, ys))
    points.update(zip(ys, xs))
    return list(points)

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
        
        
@contract(n='int,>=1', returns='tuple(*,*)')
def generate_exp_van_der_corput_sequence(n, C=1.0, mapping_function=None):
    """
        mapping_function: something that maps [0, 1] to [-inf, inf]
        
        Returns a pair of numpy arrays
        
        so that x1*x2 = C.
        
        
    """
    if C <= 0.0: # pragma: no cover
        raise_desc(ValueError, 'Need positive C, got %r.' % C)

    from .dp_inv_plus import van_der_corput_sequence
    v = np.array(van_der_corput_sequence(n))

    if mapping_function is None:
        mapping_function = lambda x: np.tan(((x - 0.5) * 2) * (np.pi / 2))
    v2 = np.array(map(mapping_function, v))
    M = np.log(C)
    logx1 = v2
    logx2 = M - v2
    finfo = np.finfo(float)

    eps = finfo.tiny
    maxi = finfo.max
    def myexp(x):
        try:
            return np.exp(x)
        except FloatingPointError:
            if x < 0:
                return eps
            else:
                return maxi

    x1 = np.array(map(myexp, logx1))
    x2 = np.array(map(myexp, logx2))
    return x1, x2

def Nat_mult_antichain_Min(m):
    """ 
        Returns the Minimal set of elements of Nat so that their product is at least m:
    
        Min { (a, b) | a * b >= m }
    
    """
    # (top, 1) or (1, top)
    P = Nat()
    P.belongs(m)
    top = P.get_top()
    if is_top(P, m):
        s = set([(top, 1), (1, top)]) # XXX:
        return s

    assert isinstance(m, int)
    
    if m == 0:
        # any (r1,r2) is such that r1*r2 >= 0
        return set([(0, 0)])
    
    s = set()
    for o1 in range(1, m + 1):
        assert o1 >= 1
        # We want the minimum x such that o1 * x >= f
        # x >= f / o1
        # x* = ceil(f / o1)
        x =  int(np.ceil(m * 1.0 / o1))
        assert x * o1 >= m
        assert (x-1) * o1 < m
        assert x >= 1
        s.add((o1, x))
    return s

def Nat_mult_antichain_Max(m):
    """ 
        Returns the set of elements of Nat so that their product is at most m:
    
        Max { (a, b) | a * b <= m }
    
    """
    # top -> [(top, top)]
    P = Nat()
    P.belongs(m)
    top = P.get_top()
    if is_top(P, m):
        s = set([(top, top)])
        return s

    assert isinstance(m, int)
    
    if m < 1:
        return set([(0, 0)])
    
    s = set()
    for o1 in range(1, m + 1):
        assert o1 >= 1
        # We want the minimum x such that o1 * x >= f
        # x >= f / o1
        # x* = ceil(f / o1)
        x =  int(np.floor(m * 1.0 / o1))
        assert x * o1 <= m # feasible
        assert (x+1) * o1 > m, (x+1, o1, m) # and minimum
        s.add((o1, x))
    return s


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
    