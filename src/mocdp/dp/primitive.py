# -*- coding: utf-8 -*-
from abc import ABCMeta, abstractmethod
from collections import namedtuple
from contracts import contract
from contracts.utils import raise_wrapped
from decent_logs import WithInternalLog
from mocdp.posets import (Map, NotBelongs, Poset, PosetProduct, Space,
    UpperSet, UpperSets)
from mocdp.posets.space_product import SpaceProduct

__all__ = [
    'PrimitiveDP',
]


class PrimitiveMeta(ABCMeta):
    # we use __init__ rather than __new__ here because we want
    # to modify attributes of the class *after* they have been
    # created
    def __init__(cls, name, bases, dct):  # @NoSelf
        ABCMeta.__init__(cls, name, bases, dct)

        if 'solve' in cls.__dict__:
            solve = cls.__dict__['solve']

            def solve2(self, f):
                F = self.get_fun_space()
                try:
                    F.belongs(f)
                except NotBelongs as e:
                    msg = "Function passed to solve() is not in function space."
                    raise_wrapped(NotBelongs, e, msg,
                                  F=F, f=f, self=self)

                try:
                    return solve(self, f)
                except NotBelongs as e:
                    raise_wrapped(NotBelongs, e,
                        'Solve failed.', self=self, f=f)
                except NotImplementedError as e:
                    raise_wrapped(NotImplementedError, e,
                        'Solve not implemented for class %s.' % name)
                return f

            setattr(cls, 'solve', solve2)



class PrimitiveDP(WithInternalLog):
    """ 
                        I = Res * M
               F      Res    M=I/Res
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

    @abstractmethod
    @contract(returns=UpperSet)
    def solve(self, func):
        '''
            Given one func point,
            Returns an UpperSet 
        '''
        pass

    @contract(ufunc=UpperSet)
    def solveU(self, ufunc):
        UF = UpperSets(self.get_fun_space())
        UF.belongs(ufunc)
        from mocdp.posets import poset_minima
        
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

    def __repr__(self):
        return '%s(%s→%s)' % (type(self).__name__, self.F, self.R)

    def repr_long(self):
        return self.__repr__()

NormalForm = namedtuple('NormalForm', ['S', 'alpha', 'beta'])


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
        return s
