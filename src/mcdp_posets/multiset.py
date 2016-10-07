# -*- coding: utf-8 -*-
from collections import defaultdict
import itertools

from contracts import contract
from contracts.utils import raise_desc
from mcdp_posets.nat import Nat, Nat_add
from mocdp.exceptions import mcdp_dev_warning, do_extra_checks

from .frozendict import frozendict2
from .poset import NotLeq, Poset
from .space import NotBelongs, NotEqual


__all__ = [
    'Multiset',
    'Multisets',
]

class Multiset():
    @contract(elements='dict(*:*,>=1)', S=Poset)
    def __init__(self, elements, S):
        N = Nat()
        
        if do_extra_checks():
            for e, howmany in elements.items():
                S.belongs(e)
                N.belongs(howmany)

        self._elements = frozendict2(elements)
        self._S = S

    def get_elements(self):
        return self._elements

    def __repr__(self):
        return 'Multiset(%r, %r)' % (self._elements, self._S)

class Multisets(Poset):
    """ 
    
    """

    @contract(S=Poset)
    def __init__(self, S):
        self.S = S
# 

    def get_top(self):
        """This can only be implemented if we can enumerate the elements of S."""
        elements = self.S.get_maximal_elements()
        data = {}
        alot = Nat().get_top()
        for e in elements:
            data[e] = alot
        return Multiset(data, self.S)

    def witness(self):
        data = {self.S.witness(): 1}
        return Multiset(data, self.S)
    
    def get_bottom(self):
        return Multiset({}, self.S)

    def __eq__(self, other):
        return isinstance(other, Multisets) and self.S == other.S

    def belongs(self, x):
        if not isinstance(x, Multiset):
            msg = 'Not a multiset.'
            raise_desc(NotBelongs, msg, x=x)
        if not x.S == self.S:
            msg = 'Different spaces.'
            raise_desc(NotBelongs, msg, x=x, mine=self.S, his=x.S)
        return True

    def check_equal(self, a, b):
        m1 = a.get_elements()
        m2 = b.get_elements()
        mcdp_dev_warning('#XXX should use S.equal()')
        if not (m1 == m2):  # XXX: should use S.equal()...
            msg = "Not equal"
            raise_desc(NotEqual, msg, elements1=m1, elements2=m2)

    def check_leq(self, a, b):
        e1 = a.get_elements()
        e2 = b.get_elements()
        for k, n in e1.items():
            if not k in e2:
                msg = 'Key is missing.'
                raise_desc(NotLeq, msg, e1=e1, e2=e2, k=k)
            if not(n <= e2[k]):
                msg = 'Not enough.'
                raise_desc(NotLeq, msg, e1=e1, e2=e2, k=k)

    def join(self, a, b):
        """ Join is the sum """
        r = defaultdict(lambda: 0)
        c = itertools.chain(a.get_elements().items(),
                            b.get_elements().items())
        for element, n in c:
            r[element] = Nat_add(r[element], n)

        r = dict(**r)
        return Multiset(r, self.S)

    def format(self, x):
        N = Nat()
        elements = x.get_elements()
        ordered = sorted(elements)
        strings = ['%s of %s' % (N.format(elements[k]), k) for k in ordered]
        contents = ", ".join(strings)
        return "{%s}" % contents

    def __repr__(self):
        return "Multisets(%r)" % self.S
