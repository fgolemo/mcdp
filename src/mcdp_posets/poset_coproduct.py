from .poset import Poset, NotLeq
from contracts import contract
from .category_coproduct import Coproduct1
from contracts.utils import raise_desc, check_isinstance

__all__ = ['PosetCoproduct']

class PosetCoproduct(Coproduct1, Poset):
    
    @contract(subs='tuple,seq[>=1]($Poset)')
    def __init__(self, subs):
        if not subs:
            raise ValueError('At least one space needed')
        for s in subs:
            check_isinstance(s, Poset)
        Coproduct1.__init__(self, subs)

        # common bottom
        self.bottom = 'B'

    def get_bottom(self):
        return self.bottom

    def belongs(self, x):
        if x == self.bottom:
            return
        Coproduct1.belongs(x)

    def check_leq(self, a, b):
        if a == self.bottom:
            return
        if b == self.bottom:
            # and a != bottom
            raise NotLeq()
        i, xi = self.unpack(a)
        j, xj = self.unpack(b)
        if i != j:
            msg = 'They belong to different sub-spaces.'
            raise_desc(NotLeq, msg)
        self.space[i].check_leq(xi, xj)
        
    def leq(self, a, b):
        if a == self.bottom:
            return True
        if b == self.bottom:
            return False

        i, xi = self.unpack(a)
        j, xj = self.unpack(b)
        return i == j and self.space[i].leq(xi, xj)
