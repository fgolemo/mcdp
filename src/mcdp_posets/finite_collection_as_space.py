# -*- coding: utf-8 -*-
from .poset import NotLeq
from .space import NotEqual, Space
from contracts.utils import raise_desc


__all__ = ['FiniteCollectionAsSpace']


class FiniteCollectionAsSpace(Space):
    """ 
        This is a Space created out of a set of arbitrary hashable
        Python objects. 
    """

    def __init__(self, universe):
        self.elements = frozenset(universe)

    def belongs(self, x):
        return x in self.elements

    def check_equal(self, a, b):
        if a == b:
            pass
        else:
            raise NotEqual('%s ≠ %s' % (a, b))

    def check_leq(self, a, b):
        if a == b:
            pass
        else:
            raise_desc(NotLeq, 'Different', a=a, b=b)

    def format(self, x):
        return x.__repr__()

    def __repr__(self):
        return "FiniteCollectionAsSpace(%s)" % self.elements
