from .primitive import ApproximableDP, PrimitiveDP
from contracts import contract
from contracts.utils import check_isinstance
from mcdp_posets import Nat, Poset  # @UnusedImport
from mcdp_posets import PosetProduct, RcompUnits
import numpy as np
from mocdp.exceptions import mcdp_dev_warning

__all__ = [
    'InvPlus2',
]

class InvPlus2(ApproximableDP):
    @contract(Rs='tuple[2],seq[2]($RcompUnits)', F=RcompUnits)
    def __init__(self, F, Rs):
        for _ in Rs:
            check_isinstance(_, RcompUnits)
        check_isinstance(F, RcompUnits)
        self.Rs = Rs
        R = PosetProduct(Rs)
        M = R[0]
        PrimitiveDP.__init__(self, F=F, R=R, M=M)

    def solve(self, f):
        mcdp_dev_warning('Needs to raise Not?')
        n = 20
        options = np.linspace(0, f, n)
        mcdp_dev_warning('FIXME: bug - are we taking into account the units?')
        s = set()
        for o in options:
            s.add((o, f - o))

        return self.R.Us(s)


    @contract(n='int,>=0')
    def get_lower_bound(self, n):
        F = self.F
        Rs = self.Rs
        return InvPlus2L(F, Rs, n)

    @contract(n='int,>=0')
    def get_upper_bound(self, n):
        F = self.F
        Rs = self.Rs
        return InvPlus2U(F, Rs, n)

    def get_implementations_f_r(self, f, r):  # @UnusedVariable
        r1, r2 = r  # @UnusedVariable
        return set([r1])

    def evaluate_f_m(self, f, m):
        return (m, f - m)

class InvPlus2L(PrimitiveDP):

    @contract(Rs='tuple[2],seq[2]($RcompUnits)', F=RcompUnits)
    def __init__(self, F, Rs, nl):
        for _ in Rs:
            check_isinstance(_, RcompUnits)
        check_isinstance(F, RcompUnits)
        R = PosetProduct(Rs)
        M = R[0]
        PrimitiveDP.__init__(self, F=F, R=R, M=M)
        self.nl = nl

    def solve(self, f):
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
        M = R[0]
        PrimitiveDP.__init__(self, F=F, R=R, M=M)
        self.nu = nu

    def solve(self, f):
        n = self.nu

        options = np.linspace(0, f, n)
        # FIXME: bug - are we taking into account the units?
        s = set()
        for o in options:
            s.add((o, f - o))
        return self.R.Us(s)
