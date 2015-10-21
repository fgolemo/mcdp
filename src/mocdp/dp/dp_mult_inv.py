from contracts import contract
from mocdp.dp import PrimitiveDP
from mocdp.posets import Poset  # @UnusedImport
from mocdp.posets import PosetProduct, SpaceProduct
from mocdp.posets.utils import poset_minima


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
        if self.F.equal(f, self.F.get_bottom()):
            return self.R.U(self.R.get_bottom())

        # print self.F, f
        raise NotImplementedError()
    
    def solve_approx(self, f, n):
        
        m = n / 2

        import numpy as np
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

