from .primitive import ApproximableDP, PrimitiveDP
from contracts import contract
from contracts.utils import check_isinstance
from mcdp_posets import Nat, Poset  # @UnusedImport
from mcdp_posets import PosetProduct, RcompUnits, poset_minima
import numpy as np
from mcdp_posets.uppersets import UpperSet

__all__ = [
    'InvMult2',
    'InvMult2U',
    'InvMult2L',
]



class InvMult2(ApproximableDP):

    @contract(Rs='tuple[2],seq[2]($Poset)')
    def __init__(self, F, Rs):
        R = PosetProduct(Rs)
        M = R[0]
        self.F = F
        self.Rs = Rs
        PrimitiveDP.__init__(self, F=F, R=R, M=M)

    def solve(self, f):
        if self.F.equal(f, self.F.get_bottom()):
            return self.R.U(self.R.get_bottom())

        n = 20
        options = np.exp(np.linspace(-2, 2, n))
        s = set()
        for o in options:
            s.add((o, f / o))

        return self.R.Us(s)

    def evaluate_f_m(self, f, m):
        if m == 0.0:
            return (0.0, 0.0)
        return (m, f / m)
    

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
        M = R[0]
        self.F = F
        self.Rs = Rs
        self.R = R
        PrimitiveDP.__init__(self, F=F, R=R, M=M)

        self.n = n

    def solve(self, f):
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
        M = R[0]
        self.F = F
        self.Rs = Rs

        PrimitiveDP.__init__(self, F=F, R=R, M=M)
        self.R = R
        self.n = n

    def solve(self, f):
        n = self.n

        if n == 1:
            points = [(0.0, 0.0)]
        elif n == 2:
            points = [(0.0, 0.0)]
        else:  
            points = set()
            pu = sorted(samplec(n - 1, f), key=lambda _: _[0])
            # print('pu: %s' % pu)
            # assert len(pu) == n - 1
            nu = len(pu)

            points.add((0.0, pu[0][1]))
            points.add((pu[-1][0], 0.0))
            for i in range(nu - 1):
                p = (pu[i][0], pu[i + 1][1])
                points.add(p)
    
        return UpperSet(minimals=points, P=self.R)
