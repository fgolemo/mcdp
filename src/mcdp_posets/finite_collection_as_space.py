# -*- coding: utf-8 -*-
import random

from contracts.utils import raise_desc

from .space import NotBelongs, NotEqual, Space


__all__ = ['FiniteCollectionAsSpace']


class FiniteCollectionAsSpace(Space):
    """ 
        This is a Space created out of a set of arbitrary hashable
        Python objects. 
    """

    def __init__(self, universe):
        self.elements = frozenset(universe)

    def belongs(self, x):
#         if isinstance(x, dict):  # unhashable
#             msg = 'Value is not hashable.'
#             raise_desc(NotBelongs, msg, x=x, elements=self.elements)
        if not x in self.elements:
            msg = 'Element does not belong to poset.'
            raise_desc(NotBelongs, msg=msg, x=x, elements=self.elements)

    def witness(self):
        n = len(self.elements)
        i = random.randint(0, n-1)
        return list(self.elements)[i]
        
    def check_equal(self, a, b):
        if a == b:
            pass
        else:
            raise NotEqual('%s ≠ %s' % (a, b))

    def format(self, x):
        return x.__repr__()

    def __repr__(self):
        return "FiniteCollectionAsSpace(%s)" % self.elements
