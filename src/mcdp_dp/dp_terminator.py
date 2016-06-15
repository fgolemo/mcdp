# -*- coding: utf-8 -*-
from .primitive import PrimitiveDP
from mcdp_posets import PosetProduct, SpaceProduct, UpperSet


__all__ = [
    'Terminator',
]

class Terminator(PrimitiveDP):
    """ Terminates a line """

    def __init__(self, F):
        R = PosetProduct(())
        M = SpaceProduct(())
        PrimitiveDP.__init__(self, F=F, R=R, M=M)

    def solve(self, func):  # @UnusedVariable
        return UpperSet([()], self.R)

    def __repr__(self):
        return 'Term(%r)' % self.F
