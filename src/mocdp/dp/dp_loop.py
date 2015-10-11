# -*- coding: utf-8 -*-
from .primitive import PrimitiveDP
from contracts.utils import check_isinstance, raise_desc, raise_wrapped
from mocdp.posets import (Map, NotLeq, PosetProduct, UpperSet, UpperSets,
    poset_minima)
import itertools



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

            funsp = self.dp1.get_fun_space()
            fU = UpperSets(funsp)

            f = [funsp.U(func)]
            r = [self.dp1.solveU(f[0])]
    #
    #         print('f', f)
    #         print('r', r)

            for _ in range(10):  # XXX
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

        check_isinstance(funsp, PosetProduct)
        check_isinstance(ressp, PosetProduct)

        if len(funsp) != 2:
            raise ValueError('funsp needs to be length 2: %s' % funsp)

        if len(ressp) != 2:
            raise ValueError('ressp needs to be length 2: %s' % ressp)

        self.F1 = funsp[0]
        self.R1 = ressp[0]
        self.R2 = funsp[1]

        if not (funsp[1]) == (ressp[1]):
            raise_desc(ValueError, "Spaces incompatible for loop",
                       funsp=funsp, ressp=ressp,
                       ressp1=ressp[1], funsp1=funsp[1])

        F = self.F1
        R = self.R1
        PrimitiveDP.__init__(self, F=F, R=R)

    def get_normal_form(self):
        """
            S0 is a Poset
            alpha0: U(F0) x S0 -> U(R0)
            beta0:  U(F0) x S0 -> S0 
        """

        S0, alpha0, beta0 = self.dp1.get_normal_form()

        R1 = self.R1
        R2 = self.R2
        F1 = self.F1
        UR2 = UpperSets(self.R2)

        S = PosetProduct((S0, UR2))
        UF1 = UpperSets(self.F1)
        UR1 = UpperSets(self.R1)
        F1R2 = PosetProduct((F1, R2))
        UF1R2 = UpperSets(F1R2)
        UR1R2 = UpperSets(PosetProduct((self.R1, R2)))
        
        """
        S = S0 x UR2 is a Poset
        alpha: UF1 x S -> UR1
        beta: UF1 x S -> S
"""
        class DPAlpha(Map):
            def __init__(self, dp):
                self.dp = dp

                dom = PosetProduct((UF1, S))
                cod = UR1
                Map.__init__(self, dom, cod)

            def _call(self, x):
                (fs, (s0, rs)) = x
                # fs is an upper set of F1
                UF1.belongs(fs)
                # rs is an upper set of R2
                UR2.belongs(rs)
                
                # alpha0: U(F0) x S0 -> U(R0)
                # alpha0: U(F1xR2) x S0 -> U(R1xR2)
                print('rs: %s' % rs)
                print('fs: %s' % fs)
                # make the dot product
                print set(itertools.product(fs.minimals, rs.minimals))
                x = UpperSet(set(itertools.product(fs.minimals, rs.minimals)), F1R2)
                # this is an elment of U(F1xR2)
                UF1R2.belongs(x)
                
                # get what alpha0 says
                y0 = alpha0((x, s0))
                # this is in UR1R2
                UR1R2.belongs(y0)
                
                # now drop to UR1
                u = set([m[0] for m in y0.minimals])
                u = poset_minima(u, R1.leq)
                a1 = UpperSet(u, R1)

                return a1


        class DPBeta(Map):
            def __init__(self, dp):
                self.dp = dp

                dom = PosetProduct((UF1, S))
                cod = S
                Map.__init__(self, dom, cod)

            def _call(self, x):
                # beta0:  U(F0) x S0 -> S0
                # beta0: U(F1xR1) x S0 -> S0 

                # beta: UF1 x S -> S
                # beta: UF1 x (S0 x UR2) -> (S0 x UR2)
                fs, (s0, rs) = x

                # fs is an upper set of F1
                UF1.belongs(fs)
                # rs is an upper set of R2
                UR2.belongs(rs)
                
                # make the dot product
                x = UpperSet(set(itertools.product(fs.minimals, rs.minimals)), F1R2)
                # this is an elment of U(F1xR2)
                UF1R2.belongs(x)
                
                # get what beta0 says
                s0p = beta0((x, s0))
                
                # get what alpha0 says
                y0 = alpha0((x, s0))
                # this is in UR1R2
                UR1R2.belongs(y0)

                # now drop to UR2
                u = [m[1] for m in y0.minimals]
                u = poset_minima(u, R2.leq)
                m1 = UpperSet(u, R2)
                
                return s0p, m1

        return S, DPAlpha(self), DPBeta(self)

    def __repr__(self):
        return 'DPloop(%s)' % self.dp1

    def solve(self, func):
        raise NotImplementedError()
#         from mocdp.posets import NotLeq, UpperSets
#
#         funsp = self.dp1.get_fun_space()
#         ressp = self.dp1.get_res_spe
#         fU = UpperSets(ressp)
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


class DPLoop0(PrimitiveDP):
    """
        This is the version in the papers
                  ______
           f1 -> |  dp  |--->r
           f2 -> |______| |
              `-----------/
    """
    def __init__(self, dp1):
        from mocdp import get_conftools_dps

        library = get_conftools_dps()
        _, self.dp1 = library.instance_smarter(dp1)

        funsp = self.dp1.get_fun_space()
        ressp = self.dp1.get_res_space()

        check_isinstance(funsp, PosetProduct)

        if len(funsp) != 2:
            raise ValueError('funsp needs to be length 2: %s' % funsp)

        if funsp[1] != ressp:
            raise_desc(ValueError, "Spaces incompatible for loop",
                       funsp=funsp, ressp=ressp,
                       ressp1=ressp[1], funsp1=funsp[1])

        F1 = funsp[0]
        F = F1
        R = ressp
        PrimitiveDP.__init__(self, F=F, R=R)

#     def get_normal_form(self):
#         """
#             S0 is a Poset
#             alpha0: U(F0) x S0 -> U(R0)
#             beta0:  U(F0) x S0 -> S0
#         """
#
#         S0, alpha0, beta0 = self.dp1.get_normal_form()
#
#         R1 = self.R1
#         R2 = self.R2
#         F1 = self.F1
#         UR2 = UpperSets(self.R2)
#
#         S = PosetProduct((S0, UR2))
#         UF1 = UpperSets(self.F1)
#         UR1 = UpperSets(self.R1)
#         F1R2 = PosetProduct((F1, R2))
#         UF1R2 = UpperSets(F1R2)
#         UR1R2 = UpperSets(PosetProduct((self.R1, R2)))
#
#         """
#         S = S0 x UR2 is a Poset
#         alpha: UF1 x S -> UR1
#         beta: UF1 x S -> S
# """
#         class DPAlpha(Map):
#             def __init__(self, dp):
#                 self.dp = dp
#
#                 dom = PosetProduct((UF1, S))
#                 cod = UR1
#                 Map.__init__(self, dom, cod)
#
#             def _call(self, x):
#                 (fs, (s0, rs)) = x
#                 # fs is an upper set of F1
#                 UF1.belongs(fs)
#                 # rs is an upper set of R2
#                 UR2.belongs(rs)
#
#                 # alpha0: U(F0) x S0 -> U(R0)
#                 # alpha0: U(F1xR2) x S0 -> U(R1xR2)
#                 print('rs: %s' % rs)
#                 print('fs: %s' % fs)
#                 # make the dot product
#                 print set(itertools.product(fs.minimals, rs.minimals))
#                 x = UpperSet(set(itertools.product(fs.minimals, rs.minimals)), F1R2)
#                 # this is an elment of U(F1xR2)
#                 UF1R2.belongs(x)
#
#                 # get what alpha0 says
#                 y0 = alpha0((x, s0))
#                 # this is in UR1R2
#                 UR1R2.belongs(y0)
#
#                 # now drop to UR1
#                 u = set([m[0] for m in y0.minimals])
#                 u = poset_minima(u, R1.leq)
#                 a1 = UpperSet(u, R1)
#
#                 return a1
#
#
#         class DPBeta(Map):
#             def __init__(self, dp):
#                 self.dp = dp
#
#                 dom = PosetProduct((UF1, S))
#                 cod = S
#                 Map.__init__(self, dom, cod)
#
#             def _call(self, x):
#                 # beta0:  U(F0) x S0 -> S0
#                 # beta0: U(F1xR1) x S0 -> S0
#
#                 # beta: UF1 x S -> S
#                 # beta: UF1 x (S0 x UR2) -> (S0 x UR2)
#                 fs, (s0, rs) = x
#
#                 # fs is an upper set of F1
#                 UF1.belongs(fs)
#                 # rs is an upper set of R2
#                 UR2.belongs(rs)
#
#                 # make the dot product
#                 x = UpperSet(set(itertools.product(fs.minimals, rs.minimals)), F1R2)
#                 # this is an elment of U(F1xR2)
#                 UF1R2.belongs(x)
#
#                 # get what beta0 says
#                 s0p = beta0((x, s0))
#
#                 # get what alpha0 says
#                 y0 = alpha0((x, s0))
#                 # this is in UR1R2
#                 UR1R2.belongs(y0)
#
#                 # now drop to UR2
#                 u = [m[1] for m in y0.minimals]
#                 u = poset_minima(u, R2.leq)
#                 m1 = UpperSet(u, R2)
#
#                 return s0p, m1
#
#         return S, DPAlpha(self), DPBeta(self)

    def __repr__(self):
        return 'DPLoop0(%s)' % self.dp1

    def solve(self, f1):
        F = self.dp1.get_fun_space()
        F1 = F[0]
        F1.belongs(f1)
        R = self.dp1.get_res_space()

        UR = UpperSets(R)
        UF = UpperSets(F)

        # we consider a set of iterates
        # we start from the bottom
        s0 = UR.get_bottom()

        S = [s0]
        
        def iterate(si):
            """ Returns the next iteration """
            # compute the product
            UR.belongs(si)
            upset = set()
            for r in si.minimals:
                upset.add((f1, r))
            upset = UpperSet(upset, F)
            UF.belongs(upset)
            # solve the 
            res = self.dp1.solveU(upset)
            UR.belongs(res)
            return res
            
        for _ in range(100):  # XXX
            # now take the product of f1
            si = S[-1]
            sip = iterate(si)

            try:
                UR.check_leq(si, sip)
            except NotLeq as e:
                msg = 'Loop iteration invariant not satisfied.'
                raise_wrapped(Exception, e, msg, si=si, sip=sip, dp=self.dp1)

            S.append(sip)

            if UR.leq(sip, si):
                print('breaking because converged')
                break 
        return S[-1]
