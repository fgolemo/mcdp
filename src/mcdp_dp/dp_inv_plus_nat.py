from mcdp_dp.primitive import PrimitiveDP
from contracts import contract
from mcdp_posets.nat import Nat
from contracts.utils import check_isinstance
from mcdp_posets.poset_product import PosetProduct

__all__ = [
    'InvPlus2Nat',
]

class InvPlus2Nat(PrimitiveDP):

    @contract(Rs='tuple[2],seq[2]($Nat)', F=Nat)
    def __init__(self, F, Rs):
        for _ in Rs:
            check_isinstance(_, Nat)
        check_isinstance(F, Nat)
        R = PosetProduct(Rs)
        M = R
        PrimitiveDP.__init__(self, F=F, R=R, I=M)

    def evaluate(self, m):
        a, b = m
        top = self.R.get_top()
        if top in (a,b):
            s = top
        else:
            s = a + b
        UR = self.R.U((a, b))
        LF = self.F.L(s)
        return LF, UR

    def solve(self, f):
        # FIXME: what about the top?
        top = self.F.get_top()
        if f == top:
            s = set([(top, 0), (0, top)])
            return self.R.Us(s)

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

