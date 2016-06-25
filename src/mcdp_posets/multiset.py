# -*- coding: utf-8 -*-
from mcdp_posets.poset import Poset, NotLeq
from contracts import contract
from mcdp_posets.space import Space, NotBelongs, NotEqual
from compmake.utils.frozen import frozendict2  # XXX
from contracts.utils import raise_desc
from mocdp.exceptions import mcdp_dev_warning
from collections import defaultdict
import itertools

__all__ = [
    'Multiset',
    'Multisets',
]

class Multiset():
    @contract(elements='dict(*:int,>=1)', S=Space)
    def __init__(self, elements, S):
        self._elements = frozendict2(elements)
        self._S = S

    def get_elements(self):
        return self.elements

    def __repr__(self):
        return 'Multiset(%r, %r)' % (self._elements, self.S)

class Multisets(Poset):
    """ 
    
    """

    @contract(S=Space)
    def __init__(self, S):
        self.S = S

# This can only be implemented if we can enumerate the elements of Space
#     def get_top(self):
#         return
#
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
            raise_desc(NotEqual, elements1=m1, elements2=m2)

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
            r[element] += n

        r = dict(**r)
        return Multiset(r, self.S)

    def format(self, x):
        elements = x.get_elements()
        ordered = sorted(elements)
        strings = ['%d of %s' % (elements[k], k) for k in ordered]
        contents = ", ".join(strings)
        return "{%s}" % contents

    def __repr__(self):
        return "Multisets(%r)" % self.S
