# -*- coding: utf-8 -*-
from .poset import NotLeq, Poset
from .space import NotBelongs, NotEqual
from contracts.utils import raise_desc
import numpy as np

__all__ = [
   'Ncomp',
]

class NcompTop():
    def __repr__(self):
        return "⊤"
    def __eq__(self, x):
        return isinstance(x, NcompTop)
    def __hash__(self):
        return 42  # "RCompTop"

class Ncomp(Poset):
    """
           N U Top 
    """
    def __init__(self):
        self.top = NcompTop()

    def get_bottom(self):
        return 0

    def get_top(self):
        return self.top

    def witness(self):
        return self.get_bottom()

    def belongs(self, x):
        if x == self.top:
            return

        if not isinstance(x, int):
            raise_desc(NotBelongs, 'Not an integer.', x=x)

        if not 0 <= x:
            msg = '%s ≰ %s' % (0, x)
            raise_desc(NotBelongs, msg, x=x)

        return

    def join(self, a, b):
        if self.leq(a, b):
            return b
        if self.leq(b, a):
            return a
        assert False

    def meet(self, a, b):
        if self.leq(a, b):
            return a
        if self.leq(b, a):
            return b
        assert False

    def get_test_chain(self, n):
        s = [self.get_bottom()]
        s.extend(np.round(sorted(np.random.rand(n - 2) * 10)))
        s.append(self.get_top())
        return s

    def __eq__(self, other):
        return isinstance(other, Ncomp)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __repr__(self):
        return "Ncomp()"

    def format(self, x):
        self.belongs(x)
        if x == self.top:
            return self.top.__repr__()
        else:
            # TODO: add parameter
            return '%d' % x

    def _leq(self, a, b):
        if a == b:
            return True
        if a == self.top:
            return False
        if b == self.top:
            return True
        return a <= b

    def check_leq(self, a, b):
        self.belongs(a)
        self.belongs(b)
        if not self._leq(a, b):
            msg = '%s ≰ %s' % (a, b)
            raise NotLeq(msg)

    def multiply(self, a, b):
        """ Multiplication, extended for top """
        if a == self.top or b == self.top:
            return self.top
        return a * b

    def add(self, a, b):
        """ Addition, extended for top """
        if a == self.top or b == self.top:
            return self.top
        return a + b

    def check_equal(self, x, y):
        if not x == y:
            raise NotEqual('%s != %s' % (x, y))
