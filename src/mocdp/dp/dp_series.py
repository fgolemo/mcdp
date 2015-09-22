# -*- coding: utf-8 -*-
from .primitive import PrimitiveDP

__all__ = [
    'Series',
]

class Series(PrimitiveDP):

    def __init__(self, dp1, dp2):
        from mocdp import get_conftools_dps
        library = get_conftools_dps()
        _, self.dp1 = library.instance_smarter(dp1)
        _, self.dp2 = library.instance_smarter(dp2)

    def get_fun_space(self):
        return self.dp1.get_fun_space()

    def get_res_space(self):
        return self.dp2.get_res_space()

    def get_tradeoff_space(self):
        return self.dp2.get_tradeoff_space()

    def solve(self, func):
        from mocdp.posets import UpperSets, UpperSet, poset_minima

        self.info('func: %s' % func)
        u1 = self.dp1.solve(func)
        ressp1 = self.dp1.get_res_space()
        tr1 = UpperSets(ressp1)
        tr1.belongs(u1)

        self.info('u1: %s' % u1)

        mins = set([])
        for u in u1.minimals:
            v = self.dp2.solve(u)
            mins.update(v.minimals)
            

        ressp = self.get_res_space()
        minimals = poset_minima(mins, ressp.leq)
        # now mins is a set of UpperSets
        tres = self.get_tradeoff_space()

        us = UpperSet(minimals, ressp)
        tres.belongs(us)

        self.info('us: %s' % us)

        return us

    def __repr__(self):
        return 'Series(%r, %r)' % (self.dp1, self.dp2)


