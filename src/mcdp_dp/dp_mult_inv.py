from .primitive import ApproximableDP, PrimitiveDP
from contracts import contract
from contracts.utils import check_isinstance
from mcdp_posets import Nat, Poset  # @UnusedImport
from mcdp_posets import PosetProduct, RcompUnits, poset_minima
import numpy as np

__all__ = [
    'InvMult2',
    'InvPlus2',
    'InvPlus2Nat',
]


class InvMult2(PrimitiveDP):

    @contract(Rs='tuple[2],seq[2]($Poset)')
    def __init__(self, F, Rs):
        R = PosetProduct(Rs)
        M = R[0]
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
    
    def solve_approx(self, f, n, nu):
        m = n / 2
        r0 = set()
        r1 = set()
        v = np.sqrt(f)
        r1.add((v, v))

        for i in range(m):
            x = v + 1 + i
            y = f / x
            r1.add((x, y))

            r1.add((y, x))

        r1.add((x, 0.0))
        r1.add((0.0, x))

        points = sorted(r1, key=lambda x: x[0])
        for i in range(len(points) - 1):

            m = (min(points[i][0], points[i + 1][0]),
                 min(points[i][1], points[i + 1][1]),)
            r0.add(m)

        r0 = poset_minima(r0, self.R.leq)
        r1 = poset_minima(r1, self.R.leq)
        R0 = self.R.Us(r0)
        R1 = self.R.Us(r1)

        return R0, R1

#         # first, find out if there are any tops
#         def is_there_a_top():
#             for Fi, fi in zip(self.F, f):
#                 if Fi.leq(Fi.get_top(), fi):
#                     return True
#             return False
#         if is_there_a_top():
#             return self.R.U(self.R.get_top())
#         mult = lambda x, y: x * y
#         r = functools.reduce(mult, f)
#         return self.R.U(r)

    def __repr__(self):
        return 'InvMult2(%s -> %s)' % (self.F, self.R)



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
        n = 20
        options = np.linspace(0, f, n)
        # FIXME: bug - are we taking into account the units?
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



class InvPlus2Nat(PrimitiveDP):

    @contract(Rs='tuple[2],seq[2]($Nat)', F=Nat)
    def __init__(self, F, Rs):
        for _ in Rs:
            check_isinstance(_, Nat)
        check_isinstance(F, Nat)
        R = PosetProduct(Rs)
        M = R[0]
        PrimitiveDP.__init__(self, F=F, R=R, M=M)

    def solve(self, f):
        # FIXME: what about the top?
        assert isinstance(f, int)

        s = set()
        for o in range(f + 1):
            s.add((o, f - o))

        return self.R.Us(s)

    def get_implementations_f_r(self, f, r):  # @UnusedVariable
        r1, r2 = r  # @UnusedVariable
        return set([r1])

    def evaluate_f_m(self, f, m):
        return (m, f - m)

    def __repr__(self):
        return 'InvPlus2Nat(%s -> %s)' % (self.F, self.R)


#     def solve_approx(self, f, n, nu):
#         m = n / 2
#         r0 = set()
#         r1 = set()
#         v = np.sqrt(f)
#         r1.add((v, v))
#
#         for i in range(m):
#             x = v + 1 + i
#             y = f / x
#             r1.add((x, y))
#
#             r1.add((y, x))
#
#         r1.add((x, 0.0))
#         r1.add((0.0, x))
#
#         points = sorted(r1, key=lambda x: x[0])
#         for i in range(len(points) - 1):
#
#             m = (min(points[i][0], points[i + 1][0]),
#                  min(points[i][1], points[i + 1][1]),)
#             r0.add(m)
#
#         r0 = poset_minima(r0, self.R.leq)
#         r1 = poset_minima(r1, self.R.leq)
#         R0 = self.R.Us(r0)
#         R1 = self.R.Us(r1)
#
#         return R0, R1

#         # first, find out if there are any tops
#         def is_there_a_top():
#             for Fi, fi in zip(self.F, f):
#                 if Fi.leq(Fi.get_top(), fi):
#                     return True
#             return False
#         if is_there_a_top():
#             return self.R.U(self.R.get_top())
#         mult = lambda x, y: x * y
#         r = functools.reduce(mult, f)
#         return self.R.U(r)

