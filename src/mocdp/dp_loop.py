from mocdp.defs import PrimitiveDP, UpperSets
from mocdp.configuration import get_conftools_dps
from contracts.utils import raise_desc



class SimpleLoop(PrimitiveDP):

    def __init__(self, dp1):
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
        funsp = self.dp1.get_fun_space()
        fU = UpperSets(funsp)

        f = [funsp.U(func)]
        r = [self.dp1.solveU(f[0])]

        for i in range(10):  # XXX
#             fi = fU.join(f[0], r[-1])
            fi = r[-1]
            ri = self.dp1.solveU(fi)

            fU.check_leq(fi, ri)

            f.append(fi)
            r.append(ri)

            if f[-1] == f[-2]:
                print('breaking because of f converged: %s' % f[-1])
                break

        print f
        print r

        return r[-1]
