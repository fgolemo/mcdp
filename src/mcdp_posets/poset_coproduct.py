from .poset import Poset, NotLeq
from contracts import contract
from .category_coproduct import Coproduct1
from contracts.utils import raise_desc, check_isinstance
from mcdp_posets.poset import NotBounded
from mocdp.exceptions import mcdp_dev_warning

__all__ = ['PosetCoproduct']

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

    def get_bottom(self):
        mcdp_dev_warning('Except one of them is empty?')
        raise NotBounded()

    def get_top(self):
        mcdp_dev_warning('Except one of them is empty?')
        raise NotBounded()

    def get_minimal_elements(self):
        S = set()
        for i, sub in enumerate(self.spaces):
            ms = sub.get_minimal_elements()
            for m in ms:
                s = self.pack(i, m)
                S.add(s)
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
        self.space[i].check_leq(xi, xj)
        
    def leq(self, a, b):
        i, xi = self.unpack(a)
        j, xj = self.unpack(b)
        return i == j and self.space[i].leq(xi, xj)
