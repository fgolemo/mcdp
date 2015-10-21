from contracts import contract
from mocdp.dp import PrimitiveDP
from mocdp.posets import Poset  # @UnusedImport
from mocdp.posets import PosetProduct, SpaceProduct


__all__ = [
    'InvMult2',
]


class InvMult2(PrimitiveDP):

    @contract(Rs='tuple[2],seq[2]($Poset)')
    def __init__(self, F, Rs):
        R = PosetProduct(Rs)
        M = SpaceProduct(())
        PrimitiveDP.__init__(self, F=F, R=R, M=M)

    def solve(self, f):
        self.F.belongs(f)

        if self.F.equal(f, self.F.get_bottom()):
            return self.R.U(self.R.get_bottom())

        # print self.F, f
        raise NotImplementedError()
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

