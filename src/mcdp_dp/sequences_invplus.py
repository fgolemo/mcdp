# -*- coding: utf-8 -*-
from contracts import contract
from contracts.utils import check_isinstance, raise_desc, raise_wrapped
from mcdp_posets import PosetProduct, is_top
from mcdp_posets.nat import Nat
from mcdp_posets.rcomp import finfo
from mcdp_posets.utils import check_minimal
from mocdp import MCDPConstants
from mocdp.exceptions import mcdp_dev_warning, do_extra_checks
import numpy as np


def invmultU_solve_options(F, R, f, n, algo):
    """ Returns a set of points in R that are on the line r1*r2=f. """
    from .dp_inv_mult import InvMult2

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
    from .dp_inv_mult import InvMult2
    assert algo in [InvMult2.ALGO_UNIFORM, InvMult2.ALGO_VAN_DER_CORPUT]
    
    if f == 0.0:
        return set([(0.0, 0.0)])

    if is_top(F, f):
        mcdp_dev_warning('FIXME Need much more thought about this')
        top1 = R[0].get_top()
        top2 = R[1].get_top()
        s = set([(top1, top2)])
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

        
@contract(n='int,>=1', returns='tuple(*,*)')
def generate_exp_van_der_corput_sequence(n, C=1.0, mapping_function=None):
    """
        mapping_function: something that maps [0, 1] to [-inf, inf]
        
        Returns a pair of numpy arrays
        
        so that x1*x2 = C.
        
        
    """
    if C <= 0.0: # pragma: no cover
        raise_desc(ValueError, 'Need positive C, got %r.' % C)

    v = np.array(van_der_corput_sequence(n))

    if mapping_function is None:
        mapping_function = lambda x: np.tan(((x - 0.5) * 2) * (np.pi / 2))
    v2 = np.array(map(mapping_function, v))
    M = np.log(C)
    logx1 = v2
    logx2 = M - v2

    eps = MCDPConstants.inv_relations_eps 
    maxi = 1 / eps
     
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


def sample_sum_lowerbound(F, R, f, n):
    """ 
        Returns a set of points in R below the line {(a,b) | a + b = f } 
        such that the line is contained in the upperclosure of the points.
        
        It uses the variable InvPlus2.ALGO to decide the type 
        of sampling.
    """
    check_isinstance(R, PosetProduct) 
    assert len(R) == 2
    
    if is_top(F, f):
            # +infinity
        top1 = R[0].get_top()
        top2 = R[1].get_top()
        return set([(top1, 0.0), (0.0, top2)])
        
    if F.leq(f, 0.0): # f == 0
        return set([(0.0, 0.0)])
        
         
    from mcdp_dp.dp_inv_plus import InvPlus2
    if InvPlus2.ALGO == InvPlus2.ALGO_VAN_DER_CORPUT:
        options = van_der_corput_sequence(n + 1)
    elif InvPlus2.ALGO == InvPlus2.ALGO_UNIFORM:
        options = np.linspace(0.0, 1.0, n + 1)
    else:
        assert False, InvPlus2.ALGO

    s = []
    for o in options:
        s.append((f * o, f * (1.0 - o)))

    options = set()
    for i in range(n):
        x = s[i][0]
        y = s[i + 1][1]
        
        a = R.meet(s[i], s[i+1])
        assert (x,y) == a, ((x,y), a)
        
        options.add((x, y))    

    return options


def van_der_corput_sequence(n):
    return sorted([1.0] + [float(van_der_corput(_)) for _ in range(n - 1)])

def van_der_corput(n, base=2):
    vdc, denom = 0, 1
    while n:
        denom *= base
        n, remainder = divmod(n, base)
        vdc += remainder * 1.0 / denom
    return vdc


def sample_sum_lowersets(F, R, f, n):
    """ 
        Returns a set of points in R *above* the line {(a,b) | a + b = f } 
        such that the line is contained in the downclosure of the points.
        
        It uses the variable InvPlus2.ALGO to decide the type of sampling.
    """
    check_isinstance(R, PosetProduct) 
    assert len(R) == 2
    
    if is_top(F, f):
        # this is not correct, however it does not form a monotone sequence
            # +infinity
        top1 = R[0].get_top()
        top2 = R[1].get_top()
        return set([(top1, top2)])
        
    if F.leq(f, 0.0): # f == 0
        return set([(0.0, 0.0)])
         
    from mcdp_dp.dp_inv_plus import InvPlus2
    if InvPlus2.ALGO == InvPlus2.ALGO_VAN_DER_CORPUT:
        options = van_der_corput_sequence(n + 1)
    elif InvPlus2.ALGO == InvPlus2.ALGO_UNIFORM:
        options = np.linspace(0.0, 1.0, n + 1)
    else:
        assert False, InvPlus2.ALGO

    s = []
    for o in options:
        try:
            s.append((f * o, f * (1.0 - o)))
        except FloatingPointError as e:
            if 'underflow' in str(e):
                # assert f <= finfo.tiny, (f, finfo.tiny) 
                mcdp_dev_warning('not sure about this')
                s.append((finfo.eps, finfo.eps))
            else:
                raise_wrapped(FloatingPointError, e, 'error', f=f, o=o)

    # the sequence s[] is ordered
    for i in range(len(s)-1):
        xs = [_[0] for _ in s]
        ys = [_[1] for _ in s]
        
        if not xs[i] < xs[i+1]:
            msg = 'Invalid sequence (s[%s].x = %s !< s[%s].x = %s.' % (i, xs[i],
                                                                   i+1, xs[i+1])
            xs2 = map(R[0].format, xs)
            ys2 = map(R[1].format, ys)
            raise_desc(AssertionError, msg, s=s, xs=xs, ys=ys, xs2=xs2, ys2=ys2)
        
    options = set()
    for i in range(n):
        x = s[i + 1][0]
        y = s[i][1] # join
        
        a = R.join(s[i], s[i+1])
        
        if (x,y) != a:
            msg = 'Numerical error'
            raise_desc(AssertionError, msg,
                       x=x, y=y, a=a, s_i=s[i], s_i_plus=s[i+1])
        options.add((x, y))    

    return options

def sample_sum_upperbound(F, R, f, nu):
    """ 
        F = X
        R = PosetProduct((X, X))
        
        Returns a set of points in R on the line {(a,b) | a + b = f }.
        
        If f = Top, F = Top.
    
        It uses the variable InvPlus2.ALGO to decide the type 
        of sampling.
    """

    if is_top(F, f):
        # +infinity
        top1 = R[0].get_top()
        top2 = R[1].get_top()
        return set([(top1, top2)])
    
    if F.leq(f, 0.0): # f == 0
        return set([(0.0, 0.0)])
    
    from mcdp_dp.dp_inv_plus import InvPlus2
    if InvPlus2.ALGO == InvPlus2.ALGO_VAN_DER_CORPUT:
        options = van_der_corput_sequence(nu)
    elif InvPlus2.ALGO == InvPlus2.ALGO_UNIFORM:
        options = np.linspace(0.0, 1.0, nu)
    else:
        assert False, InvPlus2.ALGO

    s = set()
    for o in options:
        s.add((f * o, f * (1.0 - o)))
    return s