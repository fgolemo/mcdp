from .primitive import ApproximableDP, NotSolvableNeedsApprox, PrimitiveDP
from contracts import contract
from contracts.utils import raise_desc
from mcdp_posets import Nat, Poset, PosetProduct, UpperSet
from mcdp_posets.utils import check_minimal
from mocdp.exceptions import do_extra_checks, mcdp_dev_warning
import numpy as np

_ = Nat, Poset

__all__ = [
    'InvMult2',
    'InvMult2U',
    'InvMult2L',
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

    def get_lower_bound(self, n):
        return InvMult2L(self.F, self.Rs, n)

    def get_upper_bound(self, n):
        return InvMult2U(self.F, self.Rs, n)

    def __repr__(self):
        return 'InvMult2(%s -> %s)' % (self.F, self.R)


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
        if f == 0.0:
            return  UpperSet(minimals=set([(0.0, 0.0)]), P=self.R)

        top = self.F.get_top()
        if f == top:
            mcdp_dev_warning('FIXME Need much more thought about this')
            top1 = self.Rs[0].get_top()
            top2 = self.Rs[1].get_top()
            s = set([(top1, top2)])
            return self.R.Us(s)
        if InvMult2.ALGO == InvMult2.ALGO_UNIFORM:
            ps = samplec(self.n, f)
        elif InvMult2.ALGO == InvMult2.ALGO_VAN_DER_CORPUT:
            x1, x2 = generate_exp_van_der_corput_sequence(n=self.n, C=f)
            ps = zip(x1, x2)
        else:
            assert False
            
        return UpperSet(minimals=ps, P=self.R)

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
        # TODO: check feasible
        return set([(f, r)])

    def evaluate(self, m):
        f, r = m
        ur = self.R.U(r)
        lf = self.F.L(f)
        return lf, ur

    def solve(self, f):
        if f == 0.0:
            return  UpperSet(minimals=set([(0.0, 0.0)]), P=self.R)

        top = self.F.get_top()
        if f == top:
            mcdp_dev_warning('FIXME Need much more thought about this')
            top1 = self.Rs[0].get_top()
            top2 = self.Rs[1].get_top()
            s = set([(top1, 0.0), (0.0, top2)])
            return self.R.Us(s)

        n = self.n

        if InvMult2.ALGO == InvMult2.ALGO_UNIFORM:
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


        elif InvMult2.ALGO == InvMult2.ALGO_VAN_DER_CORPUT:

            if n == 1:
                points = set([(0.0, 0.0)])
            else:
                x1, x2 = generate_exp_van_der_corput_sequence(n=self.n - 1, C=f)
                pu = zip(x1, x2)
                # ur = UpperSet(pu, self.R)
                assert len(pu) == self.n - 1, pu

                if do_extra_checks():
                    check_minimal(pu, self.get_res_space())

                nu = len(pu)
                points = []
                points.append((0.0, pu[0][1]))

                for i in range(nu - 1):
                    p = (pu[i][0], pu[i + 1][1])
                    points.append(p)

                points.append((pu[-1][0], 0.0))

                points = set(points)
        else:
            assert False

        assert len(points) == self.n, (self.n, len(points), points)

        return UpperSet(minimals=points, P=self.R)

@contract(n='int,>=1', returns='tuple(*,*)')
def generate_exp_van_der_corput_sequence(n, C=1.0, mapping_function=None):
    """
        mapping_function: something that maps [0, 1] to [-inf, inf]
        
        Returns a pair of numpy arrays
        
        so that x1*x2 = C.
    """
    if C <= 0.0:
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
