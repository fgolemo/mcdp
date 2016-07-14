# -*- coding: utf-8 -*-
from .primitive import PrimitiveDP
from mcdp_posets import LowerSet, PosetProduct, SpaceProduct, UpperSet


__all__ = [
    'Terminator',
]

class Terminator(PrimitiveDP):
    """ Terminates a line """

    def __init__(self, F):
        R = PosetProduct(())
        I = SpaceProduct(())
        PrimitiveDP.__init__(self, F=F, R=R, I=I)

    def solve(self, func):  # @UnusedVariable
        return UpperSet([()], self.R)
    
    def evaluate(self, m):
        assert m == ()
        maximals = self.F.get_maximal_elements()
        LF = LowerSet(maximals, self.F)
        UR = UpperSet([()], self.R)
        return LF, UR

    def __repr__(self):
        return 'Terminator(%r)' % self.F
