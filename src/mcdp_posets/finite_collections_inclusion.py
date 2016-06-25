# -*- coding: utf-8 -*-
from .poset import NotLeq, Poset
from .space import NotBelongs, NotEqual, Space
from contracts import contract
from contracts.utils import raise_desc

__all__ = ['FiniteCollectionsInclusion']

class FiniteCollectionsInclusion(Poset):
    """ Lattice of finite collections 
    
        The bottom is the empty set.
        The top is the entire set.
    """

    @contract(S=Space)
    def __init__(self, S):
        self.S = S

# This can only be implemented if we can enumerate the elements of Space
#     def get_top(self):
#         return
#
    def get_bottom(self):
        from .finite_collection import FiniteCollection
        return FiniteCollection(set([]), self.S)

    def __eq__(self, other):
        return isinstance(other, FiniteCollectionsInclusion) and self.S == other.S
#
#     def get_top(self):
#         x = self.P.get_top()
#         return UpperSet(set([x]), self.P)

#     def get_test_chain(self, n):
#         chain = self.P.get_test_chain(n)
#         f = lambda x: UpperSet(set([x]), self.P)
#         return map(f, chain)

    def belongs(self, x):
        from .finite_collection import FiniteCollection
        if not isinstance(x, FiniteCollection):
            msg = 'Not a finite collection: %s' % x.__repr__()
            raise_desc(NotBelongs, msg, x=x)
        if not x.S == self.S:
            msg = 'Different spaces: %s ≠ %s' % (self.S, x.S)
            raise_desc(NotBelongs, msg, x=x)
        return True

    def check_equal(self, a, b):
        m1 = a.elements
        m2 = b.elements
        if not (m1 == m2):
            raise NotEqual('%s ≠ %s' % (m1, m2))

    def check_leq(self, a, b):
        e1 = a.elements
        e2 = b.elements
        res = e1.issubset(e2)
        if not res:
            msg = 'Not included'
            raise_desc(NotLeq, msg, e1=e1, e2=e2)

    def join(self, a, b):  # union
        from mcdp_posets.finite_collection import FiniteCollection
        elements = set()
        elements.update(a.elements)
        elements.update(b.elements)
        return FiniteCollection(elements, self.S)

    def format(self, x):
        contents = ", ".join(self.S.format(m)
                        for m in sorted(x.elements))

        return "{%s}" % contents

    def __repr__(self):
        return "set-of(%r)" % self.S
