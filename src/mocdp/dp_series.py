from .defs import PrimitiveDP
from mocdp.poset_utils import poset_minima
from mocdp.defs import UpperSets

__all__ = [
    'Series',
]

class Series(PrimitiveDP):

    def __init__(self, dp1, dp2):
        from mocdp.configuration import get_conftools_dps
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
        u1 = self.dp1.solve(func)
        ressp1 = self.dp1.get_res_space()
        tr1 = UpperSets(ressp1)
        print('u1', u1)
        tr1.belongs(u1)

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

