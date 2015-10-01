# -*- coding: utf-8 -*-
from abc import ABCMeta, abstractmethod
from contracts import contract
from decent_logs.withinternallog import WithInternalLog
from mocdp.posets import Poset, Space, UpperSet, UpperSets
from mocdp.posets.poset_product import PosetProduct
from mocdp.posets.space import Map, NotBelongs
from mocdp.posets.single import Single
from contracts.utils import raise_wrapped
from collections import namedtuple

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
                    raise_wrapped(NotBelongs, e,
                                  "Function passed to solve() is not in function space.",
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
    __metaclass__ = PrimitiveMeta

    @contract(F=Space, R=Space)
    def __init__(self, F, R):
        self._inited = True
        self.F = F
        self.R = R

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
        alpha = DefaultAlphaMap(self)
        beta = DefaultBeta(self)
        return (get_S_null(), alpha, beta)

#     @abstractmethod
    def get_normal_form2(self):
        """
            S is a Poset
            alpha: U(F) x S -> U(R)
            beta:  U(F) x S -> S 
        """
        pass

NormalForm = namedtuple('NormalForm', ['S', 'alpha', 'beta'])



def get_S_null():
    Void = Single('*')
    UpperVoid = UpperSets(Void)
    return UpperVoid

class DefaultAlphaMap(Map):
    def __init__(self, dp):
        self.dp = dp
        F = self.dp.get_fun_space()
        self.S = get_S_null()
        self.D = PosetProduct((F, self.S))

    def get_domain(self):
        return self.D

    def get_codomain(self):
        return self.dp.get_tradeoff_space()

    def __call__(self, x):
        f, s = x
        assert s.minimals == set(["*"]), s
        return self.dp.solve(f)


class DefaultBeta(Map):
    def __init__(self, dp):
        self.dp = dp
        F = self.dp.get_fun_space()
        self.S = get_S_null()
        self.D = PosetProduct((F, self.S))
        self.C = self.S

    def get_domain(self):
        return self.D

    def get_codomain(self):
        return self.S

    def __call__(self, x):
        self.D.belongs(x)
        _f, s = x
        assert s.minimals == set(["*"]), s
        return s
