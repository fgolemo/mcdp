# -*- coding: utf-8 -*-
from .primitive_meta import PrimitiveMeta
from abc import abstractmethod
from collections import namedtuple
from contracts import contract
from contracts.utils import indent, raise_desc
from decent_logs import WithInternalLog
from mocdp.exceptions import do_extra_checks
from mocdp.posets import (
    Map, Poset, PosetProduct, Space, SpaceProduct, UpperSet, UpperSets,
    poset_minima)
from mocdp.posets.ncomp import Ncomp


__all__ = [
    'PrimitiveDP',
]


class NotFeasible(Exception):
    pass

class Feasible(Exception):
    pass

class PrimitiveDP(WithInternalLog):
    """ 
                        I = F * M
               F      Res    M=I/F
        Sum   RxR     R       []
    
    """
    __metaclass__ = PrimitiveMeta

    @contract(F=Space, R=Poset, M=Space)
    def __init__(self, F, R, M):
        self._inited = True
        self.F = F
        self.R = R
        self.M = M
        self.I = SpaceProduct((R, M))

    def _assert_inited(self):
        if not '_inited' in self.__dict__:
            msg = 'Class %s not inited.' % (type(self))
            raise Exception(msg)

    @contract(returns=Space)
    def get_fun_space(self):
        return self.F

    @contract(returns=Poset)
    def get_res_space(self):
        return self.R

    @contract(returns=Space)
    def get_imp_space(self):
        return self.I

    @contract(returns=Space)
    def get_imp_space_mod_res(self):
        return self.M

    @contract(returns=Poset)
    def get_tradeoff_space(self):
        return UpperSets(self.R)

    def is_feasible(self, func, m, r):
        try:
            self.check_feasible(func, m, r)
        except NotFeasible:
            return False
        else:
            return True

    def check_unfeasible(self, f, m, r):
        try:
            used = self.evaluate_f_m(f, m)
        except NotFeasible:
            return
        if self.R.leq(used, r):
            msg = 'Generic implementation of check_feasible(), says:\n'
            msg += ('f = %s -> [ m = %s ] -> used = %s <= r = %s' %
                (f, m, self.R.format(used), self.R.format(r)))
            raise_desc(Feasible, msg)

    def check_feasible(self, f, m, r):
        if do_extra_checks():
            self.F.belongs(f)
            self.M.belongs(m)
            self.R.belongs(r)
        used = self.evaluate_f_m(f, m)
        if do_extra_checks():
            self.R.belongs(used)
        if not self.R.leq(used, r):
            msg = 'Generic implementation of check_feasible(), says:\n'
            msg += 'f = %s -> [self(%s)] -> %s <~= %s' % (
                        self.F.format(f), self.M.format(m), self.R.format(used), self.R.format(r))
            raise_desc(NotFeasible, msg)  # f=f, m=m, r=r, used=used)

    def get_implementations_f_r(self, f, r):
        """ Returns the set of implementations that realize the pair (f, r).
            Returns a non-empty set or raises NotFeasible. """
        M = self.get_imp_space_mod_res()

        if isinstance(M, SpaceProduct) and len(M) == 0:
            m = ()
            self.check_feasible(f, m , r)
            return set([m])

        raise NotImplementedError(type(self).__name__)

    def evaluate_f_m(self, func, m):
        """ Returns the minimal resources needed
            by the particular implementation m 
        
            raises NotFeasible
        """
        M = self.get_imp_space_mod_res()
        if do_extra_checks():
            self.F.belongs(func)
            M.belongs(m)
        if isinstance(M, SpaceProduct) and m == ():
            rs = self.solve(func)
            minimals = list(rs.minimals)
            if len(minimals) == 1:
                return minimals[0]
            else:
                msg = 'Cannot use default evaluate_f_m() because multiple miminals.'
                raise_desc(NotImplementedError, msg,
                           classname=type(self),
                           func=func, M=M, m=m, minimals=rs.minimals)
        else:
            msg = 'Cannot use default evaluate_f_m()'
            raise_desc(NotImplementedError, msg,
                       classname=type(self), func=func, M=M, m=m,)

    @abstractmethod
    @contract(returns=UpperSet)
    def solve(self, func):
        '''
            Given one func point,
            Returns an UpperSet 
        '''
        pass

    @contract(returns='tuple($UpperSet, $UpperSet)')
    def solve_approx(self, f, nl, nu):  # @UnusedVariable
        x = self.solve(f)
        return x, x

    @contract(ufunc=UpperSet)
    def solveU_approx(self, ufunc, nl, nu):
        if do_extra_checks():
            UF = UpperSets(self.get_fun_space())
            UF.belongs(ufunc)

        R = self.get_res_space()

        res_l = set([])
        res_u = set([])
        for m in ufunc.minimals:
            l, u = self.solve_approx(m, nl, nu)
            res_u.update(u.minimals)
            res_l.update(l.minimals)

        l = R.Us(poset_minima(res_l, R.leq))
        u = R.Us(poset_minima(res_u, R.leq))
        return l, u

    @contract(ufunc=UpperSet)
    def solveU(self, ufunc):
        if do_extra_checks():
            UF = UpperSets(self.get_fun_space())
            UF.belongs(ufunc)
        
        res = set([])
        for m in ufunc.minimals:
            u = self.solve(m)
            res.update(u.minimals)
        ressp = self.get_res_space()
        minima = poset_minima(res, ressp.leq)
        return ressp.Us(minima)

    def get_normal_form(self):
        """
            S is a Poset
            alpha: U(F) x S -> U(R)
            beta:  U(F) x S -> S 
        """
        alpha = DefaultAlphaMap(self)
        beta = DefaultBeta(self)
        S = PosetProduct(())
        return NormalForm(S=S, alpha=alpha, beta=beta)

    def get_normal_form_approx(self):
        gamma = DefaultGamma(self)
        delta = DefaultDelta(self)
        S = PosetProduct(())
        return NormalFormApprox(S=S, gamma=gamma, delta=delta)


    def __repr__(self):
        return '%s(%s→%s)' % (type(self).__name__, self.F, self.R)

    def repr_long(self):
        return self.__repr__()

    def _children(self):
        l = []
        if hasattr(self, 'dp1'):
            l.append(self.dp1)
        if hasattr(self, 'dp2'):
            l.append(self.dp2)
        return tuple(l)

    def tree_long(self, n=None):
        if n is None: n = 120
        s = type(self).__name__
        S, _, _ = self.get_normal_form()
        u = lambda x: x.decode('utf-8')
        ulen = lambda x: len(u(x))

        def clip(x, n):
            s = str(x)
            unicode_string = s.decode("utf-8")
            l = len(unicode_string)
            s = s + ' ' * (n - l)
            if len(u(s)) > n:
                x = u(s)
                x = x[:n - 3] + '...'
                s = x.encode('utf-8')
            return s

        s2 = '   [F = %s  R = %s  M = %s  S = %s]' % (clip(self.F, 13),
                       clip(self.R, 10), clip(self.M, 15),
                           clip(S, 28))

        head = s + ' ' * (n - ulen(s) - ulen(s2)) + s2

        for x in self._children():
            head += '\n' + indent(x.tree_long(n - 2), '  ')

        return head




NormalForm = namedtuple('NormalForm', ['S', 'alpha', 'beta'])

NormalFormApprox = namedtuple('NormalFormApprox', ['S', 'gamma', 'delta'])


class DefaultAlphaMap(Map):
    def __init__(self, dp):
        self.dp = dp
        F = dp.get_fun_space()
        R = dp.get_res_space()
        UF = UpperSets(F)
        S = PosetProduct(())
        dom = PosetProduct((UF, S))
        cod = UpperSets(R)
        Map.__init__(self, dom, cod)

    def _call(self, x):
        F, _s = x
        Res = self.dp.solveU(F)
        return Res


class DefaultBeta(Map):
    def __init__(self, dp):
        self.dp = dp
        F = dp.get_fun_space()
        UF = UpperSets(F)

        S = PosetProduct(())
        dom = PosetProduct((UF, S))
        cod = S
        Map.__init__(self, dom, cod)

    def _call(self, x):
        _F, s = x
        # print('Beta() for %s' % (self.dp))
        # print(' f = %s s = %s -> unchanged ' % (_F, s))
        return s


class DefaultGamma(Map):
    """
    
        F x S, Nl, Nu
    """
    def __init__(self, dp):
        self.dp = dp
        F = dp.get_fun_space()
        R = dp.get_res_space()
        UF = UpperSets(F)
        UR = UpperSets(R)
        S = PosetProduct(())
        N = Ncomp()
        dom = PosetProduct((UF, S, N, N))
        cod = PosetProduct((UR, UR))
        Map.__init__(self, dom, cod)

    def _call(self, x):
        F, _s, nl, nu = x
        Res = self.dp.solveU_approx(F, nl, nu)
        return Res


class DefaultDelta(Map):
    def __init__(self, dp):
        self.dp = dp
        F = dp.get_fun_space()
        UF = UpperSets(F)

        S = PosetProduct(())
        N = Ncomp()
        dom = PosetProduct((UF, S, N, N))
        cod = PosetProduct((S, S))
        Map.__init__(self, dom, cod)

    def _call(self, x):
        _F, s, _nl, _nu = x
        # print('Beta() for %s' % (self.dp))
        # print(' f = %s s = %s -> unchanged ' % (_F, s))
        return s, s
