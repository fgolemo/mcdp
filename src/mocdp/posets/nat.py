# -*- coding: utf-8 -*-
from .poset import NotLeq, Poset
from .space import NotBelongs, NotEqual
from contracts.utils import raise_desc
from mocdp.exceptions import do_extra_checks
import numpy as np
import random

__all__ = [
   'Nat',
]

class NatTop():
    def __repr__(self):
        return "⊤"
    def __eq__(self, x):
        return isinstance(x, NatTop)
    def __hash__(self):
        return 43  # "RCompTop"

class Nat(Poset):
    """
        [0, 1, 2, 3) U {T}
    """
    def __init__(self):
        self.top = NatTop()

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
            raise_desc(NotBelongs, 'Not an int.', x=x)

        if not 0 <= x:
            msg = '%s ≰ %s' % (0, x)
            raise_desc(NotBelongs, msg, x=x)

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
        f = lambda: random.randint(1, 10)
        s.extend(sorted(f() for _ in range(n - 2)))
        s.append(self.get_top())
        return s

    def __eq__(self, other):
        return isinstance(other, Nat)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __repr__(self):
        return "ℕ"

    def format(self, x):
        if x == self.top:
            return self.top.__repr__()
        else:
            return '%d' % x

    def _leq(self, a, b):
        if a == b:
            return True
        if a == self.top:
            return False
        if b == self.top:
            return True
        return a <= b

    def leq(self, a, b):
        return self._leq(a, b)

    def check_leq(self, a, b):
        if do_extra_checks():
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
        if not (x == y):
            raise NotEqual('%s != %s' % (x, y))
