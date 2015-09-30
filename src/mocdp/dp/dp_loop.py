# -*- coding: utf-8 -*-
from .primitive import PrimitiveDP
from contracts.utils import check_isinstance, raise_desc
from mocdp.posets import Map, PosetProduct, UpperSet, UpperSets
from mocdp.posets.utils import poset_minima
import warnings


__all__ = ['DPLoop']

if False:
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

        from mocdp import get_conftools_dps

        library = get_conftools_dps()
        _, self.dp1 = library.instance_smarter(dp1)

        funsp = self.dp1.get_fun_space()
        ressp = self.dp1.get_res_space()

        self.F1 = funsp[0]
        self.R1 = ressp[0]
        self.R2 = funsp[1]

        check_isinstance(funsp, PosetProduct)
        check_isinstance(ressp, PosetProduct)

        if not funsp[1] == ressp[1]:

            raise_desc(ValueError, "Spaces incompatible for loop", funsp=funsp, ressp=ressp)

    def get_fun_space(self):
        return self.F1

    def get_res_space(self):
        return self.R1

    def get_normal_form(self):
        S0, alpha0, beta0 = self.dp1.get_normal_form()

        UpsetR2 = UpperSets(self.R2)
        S = PosetProduct((S0, UpsetR2))
        F1S = PosetProduct((self.F1, S))

        class DPAlpha(Map):
            def __init__(self, dp):
                self.dp = dp

            def get_domain(self):
                return F1S

            def get_codomain(self):
                return self.dp.get_tradeoff_space()

            def __call__(self, x):
                F1S.belongs(x)
                (f1, (s, r2s)) = x
                UpsetR2.belongs(r2s)

                D = alpha0.get_domain()

                am = set()
                for r2 in r2s.minimals:
                    y = ((f1, r2), s)
                    D.belongs(y)
                    a = alpha0(y)
                    assert isinstance(a, UpperSet)
                    am.update([x[0] for x in a.minimals])
                minimals = poset_minima(am, self.dp.R1.leq)
                a1 = UpperSet(minimals, self.dp.R1)
                # XXX
                return a1

#                     print('dp: %s %s' % (type(dp1), dp1))
#                     print('dp.F = %s' % dp1.get_fun_space())
#                     print('dp.R = %s' % dp1.get_res_space())
#                     print('dp.TR = %s' % dp1.get_tradeoff_space())
#                     print('S0: %s' % S0)
#                     print('α0: %s %s' % (type(alpha0), alpha0))
#                     print('β0: %s %s' % (type(beta0), beta0))
#
#
#                     print('F1S: %s ' % F1S)
#                     print('x = %s' % str(x))
#                     print('y = %s' % str(y))
#                     print('domain(alpha0) = %s' % D)

        class DPBeta(Map):
            def __init__(self, dp):
                self.dp = dp

            def get_domain(self):
                return F1S

            def get_codomain(self):
                return S

            def __call__(self, x):
                (f1, (s, r2s)) = x
                UpsetR2.belongs(r2s)

                am = set()
                bm = set()
                for r2 in r2s.minimals:
                    a = alpha0(((f1, r2), s))
                    b = beta0(((f1, r2), s))
                    
                    S0.belongs(b)
                    assert isinstance(a, UpperSet)

#  S = PosetProduct((S0, UpsetR2))

                    am.update([x[1] for x in a.minimals])

                    assert isinstance(b, UpperSet)
                    bm.update([x for x in b.minimals])
#
#
#                 print 'am: %s' % am
#                 print 'bm: %s' % bm

                au = poset_minima(am, self.dp.R2.leq)
                bu = poset_minima(bm, S0.leq)
                
#                 print 'au:', au
#                 print 'bu:', bu
#
                a2 = UpperSet(au, self.dp.R2)


                warnings.warn('Should double check this: S0.P - assert UpperSets(S0)?')
                b = UpperSet(bu, S0.P)

#                     only = [x[1] for x in a.minimals]
#                     minimals = poset_minima(only, self.dp.R1.leq)

#                 a2 = UpperSet(minimals, self.dp.R1)
                    # XXX
                return (b, a2)

        return S, DPAlpha(self), DPBeta(self)

    def __repr__(self):
        return 'DPloop(%s)' % self.dp1

    def solve(self, func):
        raise NotImplementedError()
#         from mocdp.posets import NotLeq, UpperSets
#
#         funsp = self.dp1.get_fun_space()
#         fU = UpperSets(funsp)
#
#         f = [funsp.U(func)]
#         q = [self.R2.get_bottom()]
#
# #
# #         print('f', f)
# #         print('r', r)
#
#         for i in range(10):  # XXX
# #             fi = fU.join(f[0], r[-1])
#             fi = r[-1]
# #             print('fi', fi)
#             ri = self.dp1.solveU(fi)
# #             print('ri', ri)
#             f.append(fi)
#             r.append(ri)
#
#             if f[-1] == f[-2]:
#                 print('breaking because of f converged: %s' % f[-1])
#                 break
# #
# #         print f
# #         print r
#
#         return r[-1]

