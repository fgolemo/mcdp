# -*- coding: utf-8 -*-
from contracts.utils import raise_wrapped
import numpy as np

from .poset import NotLeq, Poset
from .space import NotBelongs, NotEqual


__all__ = [
   'Interval',
   'GenericInterval',
]

class GenericInterval(Poset):
    """ The interval [a, b] in the poset P. """
    def __init__(self, P, a, b):
        self.P = P
        self.a = a
        self.b = b

        # make sure that the interval is not empty
        self.P.check_leq(a, b)

    def __repr__(self):
        return 'GenericInterval(%r,%r,%r)' % (self.P, self.a, self.b)

    def witness(self):
        return self.a

    def get_bottom(self):
        return self.a

    def get_top(self):
        return self.b

    def belongs(self, x):
        self.P.belongs(x)
        try:
            self.check_leq(self.a, x)
            self.check_leq(x, self.b)
        except NotLeq as e:
            msg = 'Does not belong to interval.'
            raise_wrapped(NotBelongs, e, msg, compact=True)
             
    def check_equal(self, a, b):
        self.P.check_equal(a, b)

    def check_leq(self, a, b):
        return self.P.check_leq(a, b)

    def format(self, x):
        return self.P.format(x)


class Interval(Poset):
    def __init__(self, L, U):
        assert L <= U
        self.L = float(L)
        self.U = float(U)
        self.belongs(self.L)
        self.belongs(self.U)
        assert self.leq(self.L, self.U)

    def witness(self):
        return self.L

    def get_test_chain(self, n):
        res = np.linspace(self.L, self.U, n)
        return list(res)

    def get_bottom(self):
        return self.L

    def get_top(self):
        return self.U

    def check_equal(self, a, b):
        if not (a == b):
            raise NotEqual('%s != %s' % (a, b))

    def check_leq(self, a, b):
        if not(a <= b):
            raise NotLeq('%s ≰ %s' % (a, b))

    def belongs(self, x):
        if not isinstance(x, float):
            raise NotBelongs('Not a float: {}'.format(x))
        if not self.L <= x <= self.U:
            msg = '%s ∉ [%s, %s]' % (x, self.format(self.L),
                                     self.format(self.U))
            raise NotBelongs(msg)

    def format(self, x):
        return '%.3f' % x

    def __repr__(self):
        return "[%s,%s]" % (self.L, self.U)
