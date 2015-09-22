# -*- coding: utf-8 -*-
from .poset import NotLeq, Poset
from .space import NotBelongs
from contracts import check_isinstance
import numpy as np

__all__ = [
   'Interval',
]


class Interval(Poset):
    def __init__(self, L, U):
        assert L <= U
        self.L = float(L)
        self.U = float(U)
        self.belongs(self.L)
        self.belongs(self.U)
        assert self.leq(self.L, self.U)

    def get_test_chain(self, n):
        res = np.linspace(self.L, self.U, n)
        return list(res)

    def get_bottom(self):
        return self.L

    def get_top(self):
        return self.U

    def check_leq(self, a, b):
        if not(a <= b):
            raise NotLeq('%s ≰ %s' % (a, b))

    def belongs(self, x):
        check_isinstance(x, float)
        if not self.L <= x <= self.U:
            msg = '%s ∉ [%s, %s]' % (x, self.format(self.L),
                                     self.format(self.U))
            raise NotBelongs(msg)
        return True

    def format(self, x):
        return '%.3f' % x

    def __repr__(self):
        return "[%s,%s]" % (self.L, self.U)
