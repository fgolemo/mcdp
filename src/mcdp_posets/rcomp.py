# -*- coding: utf-8 -*-
from .poset import NotLeq, Poset
from contracts.utils import raise_desc
from .space import NotBelongs, NotEqual
from mocdp.exceptions import do_extra_checks
import numpy as np


__all__ = [
   'Rcomp',
]

class RcompTop():
    def __str__(self):
        return self.__repr__()
    def __repr__(self):
        # return "⊤"
        return "∞"
    def __eq__(self, x):
        return isinstance(x, RcompTop)
    def __hash__(self):
        return 42  # "RCompTop"

    # used for visualization
    def __float__(self):
        return np.inf

finfo = np.finfo(float)
tiny = finfo.tiny
eps = finfo.eps
maxf = finfo.max

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
        if not np.isfinite(x):
            msg = 'Not finite and not equal to top (%s).' % self.top
            raise_desc(NotBelongs, msg, x=x)
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
            # TODO: add parameter
            if x == int(x):
                return '%d' % int(x)
            else:
                if x == tiny:
                    return 'tiny'

                if x == eps:
                    return 'eps'

                if x == maxf:
                    return 'max'

                s = '%.5f' % x
                s = '%.10f' % x
                # s = '%f' % x
                # remove trailing 0s
                s = s.rstrip('0')
                return s

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
        if not x == y:
            raise NotEqual('%s != %s' % (x, y))
