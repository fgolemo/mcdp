from .primitive import ApproximableDP, PrimitiveDP
from contracts import contract
from contracts.utils import check_isinstance, raise_desc
from mcdp_dp.primitive import NotSolvableNeedsApprox
from mcdp_posets import Nat, Poset, PosetProduct, RcompUnits, get_types_universe
from mocdp.exceptions import DPInternalError, mcdp_dev_warning

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

        tu = get_types_universe()
        if not tu.equal(Rs[0], Rs[1]) or not tu.equal(F, Rs[0]):
            msg = 'InvPlus only available for consistent units.'
            raise_desc(DPInternalError, msg, F=F, Rs=Rs)

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

        options = van_der_corput_sequence(n + 1)

        s = []
        for o in options:
            s.append((f * o, f * (1 - o)))

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

        options = van_der_corput_sequence(n)

        # FIXME: bug - are we taking into account the units?
        s = set()
        for o in options:
            s.add((f * o, f * (1 - o)))
        return self.R.Us(s)

def van_der_corput_sequence(n):
    return sorted([1.0] + [float(van_der_corput(_)) for _ in range(n - 1)])

def van_der_corput(n, base=2):
    vdc, denom = 0, 1
    while n:
        denom *= base
        n, remainder = divmod(n, base)
        vdc += remainder * 1.0 / denom
    return vdc
