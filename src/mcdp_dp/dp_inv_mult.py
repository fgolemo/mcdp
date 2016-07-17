from .primitive import ApproximableDP, PrimitiveDP
from contracts import contract
from mcdp_dp.primitive import NotSolvableNeedsApprox
from mcdp_posets import Nat, Poset  # @UnusedImport
from mcdp_posets import PosetProduct, UpperSet
import numpy as np
from mocdp.exceptions import mcdp_dev_warning

__all__ = [
    'InvMult2',
    'InvMult2U',
    'InvMult2L',
]


class InvMult2(ApproximableDP):

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

    def solve(self, f):
        top = self.F.get_top()
        if f == top:
            mcdp_dev_warning('FIXME Need much more thought about this')
            top1 = self.Rs[0].get_top()
            top2 = self.Rs[1].get_top()
            s = set([(top1, top2)])
            return self.R.Us(s)

        ps = samplec(self.n, f)
        return UpperSet(minimals=ps, P=self.R)

def samplec(n, c):
    ps = sample(n)
    s = np.sqrt(c)
    ps = [(x * s, y * s) for x, y in ps]
    return ps

@contract(n='int,>=1', returns='list(tuple(float, float))')
def sample(n):
    """ Samples n points on the curve xy=1 """
    assert n >= 1
    points = set()
    points.add((1.0, 1.0))
    # divide the interval [0,1] equally in n/2 intervals
    m = n / 2
    xs = np.linspace(0.0, 1.0, m + 2)[1:-1]
    ys = 1.0 / xs
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


    def evaluate(self, m):
        f, r = m
        ur = self.R.U(r)
        lf = self.F.L(f)
        return lf, ur

    def solve(self, f):
        top = self.F.get_top()
        if f == top:
            mcdp_dev_warning('FIXME Need much more thought about this')
            top1 = self.Rs[0].get_top()
            top2 = self.Rs[1].get_top()
            s = set([(top1, 0.0), (0.0, top2)])
            return self.R.Us(s)

        n = self.n

        if n == 1:
            points = [(0.0, 0.0)]
        elif n == 2:
            points = [(0.0, 0.0)]
        else:  
            points = set()
            pu = sorted(samplec(n - 1, f), key=lambda _: _[0])
            # assert len(pu) == n - 1
            nu = len(pu)

            points.add((0.0, pu[0][1]))
            points.add((pu[-1][0], 0.0))
            for i in range(nu - 1):
                p = (pu[i][0], pu[i + 1][1])
                points.add(p)

            # s = " ".join(['%s*%s=%s ' % (a, b, a * b) for a, b in sorted(points, key=lambda _: _[0])])

        return UpperSet(minimals=points, P=self.R)
