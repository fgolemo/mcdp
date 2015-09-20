from .defs import PrimitiveDP
from mocdp.poset_utils import poset_minima

__all__ = [
    'Series',
]

class Series(PrimitiveDP):

    def __init__(self, dp1, dp2):
        self.dp1 = dp1
        self.dp2 = dp2

    def get_fun_space(self):
        return self.dp1.get_fun_space()

    def get_res_space(self):
        return self.dp2.get_res_space()

    def get_tradeoff_space(self):
        return self.dp2.get_tradeoff_space()

    def solve(self, func):
        u1 = self.dp1.solve(func)

        mins = set([])
        for u in u1.minimals:
            v = self.dp2.solve(u)
            mins.update(v.minimals)
            
        ressp = self.get_res_space()
        minimals = poset_minima(mins, ressp.leq)
        # now mins is a set of UpperSets
        tres = self.get_tradeoff_space()
        from mocdp.defs import UpperSet
        us = UpperSet(minimals, ressp)
        tres.belongs(us)
        return us

