from .primitive import ApproximableDP, PrimitiveDP
from contracts import contract
from contracts.utils import check_isinstance
from mcdp_dp.primitive import NotSolvableNeedsApprox
from mcdp_posets import Nat, Poset, PosetProduct, RcompUnits
from mocdp.exceptions import mcdp_dev_warning
import numpy as np

_ = Nat, Poset

__all__ = [
    'InvPlus2',
    'InvPlus2U',
    'InvPlus2L',
]

mcdp_dev_warning('FIXME: bug - are we taking into account the units?')

class InvPlus2(ApproximableDP):
    @contract(Rs='tuple[2],seq[2]($RcompUnits)', F=RcompUnits)
    def __init__(self, F, Rs):
        for _ in Rs:
            check_isinstance(_, RcompUnits)
        check_isinstance(F, RcompUnits)
        self.Rs = Rs
        R = PosetProduct(Rs)
        mcdp_dev_warning('Should I use the empty set?')
        M = PosetProduct((F, R))
        PrimitiveDP.__init__(self, F=F, R=R, I=M)

    def solve(self, f):
        raise NotSolvableNeedsApprox(type(self))

    def evaluate(self, m):
        raise NotSolvableNeedsApprox(type(self))

    @contract(n='int,>=0')
    def get_lower_bound(self, n):
        F = self.F
        Rs = self.Rs
        dp = InvPlus2L(F, Rs, n)
        # preserve_dp_attributes(self, dp)
        return dp

    @contract(n='int,>=0')
    def get_upper_bound(self, n):
        F = self.F
        Rs = self.Rs
        dp = InvPlus2U(F, Rs, n)
        # preserve_dp_attributes(self, dp)
        return dp

    def get_implementations_f_r(self, f, r):  # @UnusedVariable
        raise NotSolvableNeedsApprox(type(self))


class InvPlus2L(PrimitiveDP):

    @contract(Rs='tuple[2],seq[2]($RcompUnits)', F=RcompUnits)
    def __init__(self, F, Rs, nl):
        for _ in Rs:
            check_isinstance(_, RcompUnits)
        check_isinstance(F, RcompUnits)
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
        if self.F.equal(f, self.F.get_top()):
            # +infinity
            top1 = self.R[0].get_top()
            top2 = self.R[1].get_top()
            s = set([(top1, 0.0), (0.0, top2)])
            return self.R.Us(s)
        n = self.nl
        o0 = np.linspace(0, f, n + 1)
        # FIXME: bug - are we taking into account the units?
        s = []
        for o in o0:
            s.append((o, f - o))

        options = set()
        for i in range(n):
            x = s[i][0]
            y = s[i + 1][1]
            options.add((x, y))

        return self.R.Us(options)


class InvPlus2U(PrimitiveDP):

    @contract(Rs='tuple[2],seq[2]($RcompUnits)', F=RcompUnits)
    def __init__(self, F, Rs, nu):
        for _ in Rs:
            check_isinstance(_, RcompUnits)
        check_isinstance(F, RcompUnits)
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

        if self.F.equal(f, self.F.get_top()):
            # +infinity
            top1 = self.R[0].get_top()
            top2 = self.R[1].get_top()
            s = set([(top1, 0.0), (0.0, top2)])
            return self.R.Us(s)

        n = self.nu

        options = np.linspace(0, f, n)
        # FIXME: bug - are we taking into account the units?
        s = set()
        for o in options:
            s.add((o, f - o))
        return self.R.Us(s)
