# -*- coding: utf-8 -*-
from .primitive import PrimitiveDP
from contracts.utils import raise_desc, check_isinstance
from mocdp.posets.poset_product import PosetProduct


__all__ = ['SimpleLoop', 'DPLoop']

class SimpleLoop(PrimitiveDP):

    def __init__(self, dp1):
        from mocdp import get_conftools_dps

        library = get_conftools_dps()
        _, self.dp1 = library.instance_smarter(dp1)

        funsp = self.get_fun_space()
        ressp = self.get_res_space()

        if not funsp == ressp:
            raise_desc(ValueError, "Need exactly same space", funsp=funsp, ressp=ressp)

    def get_fun_space(self):
        return self.dp1.get_fun_space()

    def get_res_space(self):
        return self.dp1.get_res_space()

    def solve(self, func):
        from mocdp.posets import NotLeq, UpperSets

        funsp = self.dp1.get_fun_space()
        fU = UpperSets(funsp)

        f = [funsp.U(func)]
        r = [self.dp1.solveU(f[0])]
#
#         print('f', f)
#         print('r', r)

        for i in range(10):  # XXX
#             fi = fU.join(f[0], r[-1])
            fi = r[-1]
#             print('fi', fi)
            ri = self.dp1.solveU(fi)
#             print('ri', ri)

            if False:
                try:
                    fU.check_leq(fi, ri)
                except NotLeq as e:
                    msg = 'Loop iteration invariant not satisfied.'
                    msg += '\n %s <= %s: %s' % (fi, ri, e)
                    raise_desc(Exception, msg, fi=fi, ri=ri, dp=self.dp1)

            f.append(fi)
            r.append(ri)

            if f[-1] == f[-2]:
                print('breaking because of f converged: %s' % f[-1])
                break
#
#         print f
#         print r

        return r[-1]



class DPLoop(PrimitiveDP):

    def __init__(self, dp1):
        print('here')

        from mocdp import get_conftools_dps

        library = get_conftools_dps()
        _, self.dp1 = library.instance_smarter(dp1)

        funsp = self.dp1.get_fun_space()
        ressp = self.dp1.get_res_space()

        check_isinstance(funsp, PosetProduct)
        check_isinstance(ressp, PosetProduct)

        if not funsp[1] == ressp[1]:

            raise_desc(ValueError, "Spaces incompatible for loop", funsp=funsp, ressp=ressp)

        self.F = funsp[0]
        self.R = ressp[0]
        self.Rloop = funsp[1]

    def get_fun_space(self):
        return self.F

    def get_res_space(self):
        return self.R

    def solve(self, func):
        raise NotImplementedError()
        from mocdp.posets import NotLeq, UpperSets

        funsp = self.dp1.get_fun_space()
        fU = UpperSets(funsp)

        f = [funsp.U(func)]
        q = [self.Rloop.get_bottom()]

#
#         print('f', f)
#         print('r', r)

        for i in range(10):  # XXX
#             fi = fU.join(f[0], r[-1])
            fi = r[-1]
#             print('fi', fi)
            ri = self.dp1.solveU(fi)
#             print('ri', ri)
            f.append(fi)
            r.append(ri)

            if f[-1] == f[-2]:
                print('breaking because of f converged: %s' % f[-1])
                break
#
#         print f
#         print r

        return r[-1]

