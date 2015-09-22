# -*- coding: utf-8 -*-
from abc import ABCMeta, abstractmethod
from contracts import contract
from decent_logs.withinternallog import WithInternalLog
from mocdp.posets import Poset, Space, UpperSet, UpperSets

__all__ = [
    'PrimitiveDP',
]


class PrimitiveDP(WithInternalLog):
    __metaclass__ = ABCMeta

    @abstractmethod
    @contract(returns=Space)
    def get_fun_space(self):
        pass

    @abstractmethod
    @contract(returns=Poset)
    def get_res_space(self):
        pass

    @contract(returns=Poset)
    def get_tradeoff_space(self):
        return UpperSets(self.get_res_space())

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
