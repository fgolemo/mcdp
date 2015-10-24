# -*- coding: utf-8 -*-
from .poset import NotLeq, Poset
from .space import NotBelongs, NotEqual
from contracts.utils import raise_desc
import numpy as np

__all__ = [
   'Rcomp',
]

class RcompTop():
    def __repr__(self):
        return "⊤"
    def __eq__(self, x):
        return isinstance(x, RcompTop)
    def __hash__(self):
        return 42  # "RCompTop"

class Rcomp(Poset):
    """
        [0, inf) U {T}
    """
    def __init__(self):
        self.top = RcompTop()

    def get_bottom(self):
        return 0.0

    def get_top(self):
        return self.top

    def witness(self):
        return self.get_bottom()

    def belongs(self, x):
        if x == self.top:
            return True

        if not isinstance(x, float):
            raise_desc(NotBelongs, 'Not a float.', x=x)

        if not 0 <= x:
            msg = '%s ≰ %s' % (0, x)
            raise_desc(NotBelongs, msg, x=x)

        return True

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
        s.extend(sorted(np.random.rand(n - 2) * 10))
        s.append(self.get_top())
        return s

    def __eq__(self, other):
        return isinstance(other, Rcomp)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __repr__(self):
#         return "ℜ ⋃ {⊤}"
#         return "ℜ"
        return "Rcomp()"

    def format(self, x):
        self.belongs(x)
        if x == self.top:
            return self.top.__repr__()
        else:
            # return '%.3f' % x
            return '%.7f' % x

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
