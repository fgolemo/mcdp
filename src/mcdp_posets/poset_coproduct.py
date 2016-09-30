import random

from contracts import contract
from contracts.utils import raise_desc, check_isinstance
from mocdp.exceptions import mcdp_dev_warning

from .category_coproduct import Coproduct1, Coproduct1Labels
from .poset import NotBounded, Poset, NotLeq


__all__ = [
    'PosetCoproduct',
    'PosetCoproductWithLabels',
]

class PosetCoproduct(Coproduct1, Poset):
    
    @contract(subs='tuple,seq[>=1]($Poset)')
    def __init__(self, subs):
        if not subs:
            raise ValueError('At least one space needed')
        for s in subs:
            check_isinstance(s, Poset)
        Coproduct1.__init__(self, subs)

    def __eq__(self, b):
        return isinstance(b, PosetCoproduct) and b.spaces == self.spaces

    def get_test_chain(self, n):
        i = random.randint(0, len(self.spaces) - 1)
        chain = self.spaces[i].get_test_chain(n)
        return list(self._packs(i, chain))

    def get_bottom(self):
        mcdp_dev_warning('Except one of them is empty?')
        raise NotBounded()

    def get_top(self):
        mcdp_dev_warning('Except one of them is empty?')
        raise NotBounded()

    def _packs(self, i, elements):
        """ packs all elements as belonging to i-th. yields a sequence """
        for m in elements:
            yield self.pack(i, m)
    
    def get_minimal_elements(self):
        S = set()
        for i, sub in enumerate(self.spaces):
            S.update(self._packs(i, sub.get_minimal_elements()))
        return S

    def get_maximal_elements(self):
        S = set()
        for i, sub in enumerate(self.spaces):
            ms = sub.get_maximal_elements()
            for m in ms:
                s = self.pack(i, m)
                S.add(s)
        return S

    def check_leq(self, a, b):
        i, xi = self.unpack(a)
        j, xj = self.unpack(b)
        if i != j:
            msg = 'They belong to different sub-spaces.'
            raise_desc(NotLeq, msg)
        self.spaces[i].check_leq(xi, xj)
        
    def leq(self, a, b):
        i, xi = self.unpack(a)
        j, xj = self.unpack(b)
        return i == j and self.spaces[i].leq(xi, xj)

 
class PosetCoproductWithLabels(Coproduct1Labels, Poset):
 
    @contract(subs='tuple,seq[>=1]($Poset)')
    def __init__(self, subs, labels):
        if not subs:
            raise ValueError('At least one space needed')
        for s in subs:
            check_isinstance(s, Poset)
        Coproduct1Labels.__init__(self, subs, labels)
 
    def __eq__(self, b):
        return (isinstance(b, PosetCoproduct) and
                b.spaces == self.spaces and
                b.labels == self.labels)
 
    def get_test_chain(self, n):
        i = random.randint(0, len(self.spaces) - 1)
        chain = self.spaces[i].get_test_chain(n)
        return list(self._packs(i, chain))
 
    def get_bottom(self):
        mcdp_dev_warning('Except one of them is empty?')
        raise NotBounded()
 
    def get_top(self):
        mcdp_dev_warning('Except one of them is empty?')
        raise NotBounded()
 
    def _packs(self, label, elements):
        """ packs all elements as belonging to i-th. yields a sequence """
        for m in elements:
            yield self.pack(label, m)
 
    def get_minimal_elements(self):
        S = set()
        for (label, sub) in zip(self.labels, self.spaces):
            S.update(self._packs(label, sub.get_minimal_elements()))
        return S
 
    def get_maximal_elements(self):
        S = set()
        for (label, sub) in zip(self.labels, self.spaces):
            S.update(self._packs(label, sub.get_maximal_elements()))
        return S
 
    def check_leq(self, a, b):
        i, xi = self.unpack(a)
        j, xj = self.unpack(b)
        if i != j:
            msg = 'They belong to different sub-spaces.'
            raise_desc(NotLeq, msg)
        self.spaces[i].check_leq(xi, xj)
 
    def leq(self, a, b):
        i, xi = self.unpack(a)
        j, xj = self.unpack(b)
        return i == j and self.spaces[i].leq(xi, xj)
