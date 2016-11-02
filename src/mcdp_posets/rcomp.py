# -*- coding: utf-8 -*-
import functools

from contracts.utils import raise_desc
from mocdp.exceptions import do_extra_checks, mcdp_dev_warning, DPInternalError
import numpy as np

from .poset import NotLeq, Poset, is_top
from .space import NotBelongs, NotEqual
from mocdp import MCDPConstants


__all__ = [
   'Rcomp',
]

class RcompTop():
    def __str__(self):
        return self.__repr__()
    def __repr__(self):
        # return "⊤"
        return "+∞"
    def __eq__(self, x):
        return isinstance(x, RcompTop)
    def __hash__(self):
        return 42  # "RCompTop"

    # used for visualization
    def __float__(self):
        return np.inf

class RcompBottom():
    def __str__(self):
        return self.__repr__()
    def __repr__(self):
        # return "⊤"
        return "-∞"
    def __eq__(self, x):
        return isinstance(x, RcompBottom)
    def __hash__(self):
        return 42  # "RCompTop"
    # used for visualization
    def __float__(self):
        return -np.inf

finfo = np.finfo(float)
# tiny = finfo.tiny
# eps = finfo.eps
# maxf = finfo.max

class RcompBase(Poset):
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
        return 2.0

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
        def f():
            """ Random number between 0 and 10, up to 2 significant digits. """
            x = np.random.rand() * 10
            precision = 10
            x = np.round(x * precision) / precision
            return float(x)
        
        if n >= 3:
            other = []
            
            some = []
            if MCDPConstants.Rcomp_chain_include_tiny:
                some.append(finfo.tiny)
            if MCDPConstants.Rcomp_chain_include_eps:
                some.append(finfo.eps)
            if MCDPConstants.Rcomp_chain_include_max:
                some.append(finfo.max)
                
            some = [0.1, 1.0, 0.9, 1.1, 2.0, 2.1]
            have = len(some)
            other.extend(some[:n-2])
            
            remaining = have - (n-2)
            if remaining > 0:
                while remaining:
                    x = f()
                    if x in other or x in s:
                        continue
                    other.append(x)
                    remaining -= 1
                
            s.extend(sorted(other))
        s.append(self.get_top())
        return s

    def format(self, x):
        if do_extra_checks():
            self.belongs(x)

        if x == self.top:
            return self.top.__repr__()
        else:
            # TODO: add parameter
            if x == int(x):
                return '%d' % int(x)
            else:
                if x == finfo.tiny:
                    return 'tiny'

                if x == finfo.eps:
                    return 'eps'

                if x == finfo.max:
                    return 'max'

                # s = '%.5f' % x
                # s = '%.10f' % x
                s = '%f' % x
                
                # remove trailing 0s
                s = s.rstrip('0')
                return s

    tolerate_numerical_errors = False 
    
    def _leq(self, a, b):
        if a == b:
            return True
        if a == self.top:
            return False
        if b == self.top:
            return True
        
        if Rcomp.tolerate_numerical_errors:
            if bool(np.isclose(a, b, rtol=0)):
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


    def add(self, a, b):
        """ Addition, extended for top """
        if a == self.top or b == self.top:
            return self.top
        mcdp_dev_warning('overflow check')
        return a + b

    def check_equal(self, x, y):
        if not x == y:
            raise NotEqual('%s != %s' % (x, y))

class Rcomp(RcompBase):
    """ This is used as a separate class so Rcompunits does not
    derive from Rcomp (which might confuse tests using isinstance) """
    
    def __eq__(self, other):
        return isinstance(other, Rcomp)

    def __ne__(self, other):
        return not self.__eq__(other)
    
    def __repr__(self):
#         return "ℜ ⋃ {⊤}"
#         return "ℜ"
        return "Rcomp()"



class Rbicomp(Poset):
    """
        -inf U R U  {T}
    """
    def __init__(self):
        self.top = RcompTop()
        self.bottom = RcompBottom()

    def get_bottom(self):
        return self.bottom

    def get_top(self):
        return self.top

    def witness(self):
        return 0.0

    def belongs(self, x):
        if x == self.top:
            return
        if x == self.bottom:
            return

        if not isinstance(x, float):
            raise_desc(NotBelongs, 'Not a float.', x=x)
        if not np.isfinite(x):
            msg = 'Not finite and not equal to top or bottom.'
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
        s.extend(sorted(np.random.rand(n - 2) * 10))
        s.append(self.get_top())
        return s

    def __eq__(self, other):
        return isinstance(other, Rcomp)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __repr__(self):
        return "Rbicomp()"

    def format(self, x):
        self.belongs(x)

        if x == self.top:
            return self.top.__repr__()
        elif x == self.bottom:
            return self.bottom.__repr__()
        else:
            assert isinstance(x, float)
            # TODO: add parameter
            if x == int(x):
                return '%d' % int(x)
            else:
                if x == finfo.tiny:
                    return 'tiny'

                if x == finfo.eps:
                    return 'eps'

                if x == finfo.max:
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
        if a == self.bottom:
            return True
        if b == self.top:
            return True
        if b == self.bottom:
            return False
        return a <= b

    def leq(self, a, b):
        return self._leq(a, b)

    def check_leq(self, a, b):
        if not self._leq(a, b):
            msg = '%s ≰ %s' % (a, b)
            raise NotLeq(msg) 

    def check_equal(self, x, y):
        if not x == y:
            raise NotEqual('%s != %s' % (x, y))


def Rcomp_multiply_upper_topology_seq(As, values, C):
    """
        As: tuple of Rcompunits
        values: values (values[i] in A[i])
        C: result
    """
    def mult2(x, y):
        from mcdp_posets.rcomp_units import mult_table
        A, a = x
        B, b = y
        if isinstance(A, Rcomp):
            Y = A
        else:
            Y = mult_table(A, B)
        y = Rcomp_multiply_upper_topology(A, a, B, b, Y)
        return (Y, y) 
    
    ops = zip(As, values)
    (Cobt, value) = functools.reduce(mult2, ops)
    
    from mcdp_posets.rcomp_units import RcompUnits
    if isinstance(C, RcompUnits):
        if Cobt.units != C.units:
            msg = 'Expected %s, obtained %s.' % (C, Cobt)
            raise_desc(DPInternalError, msg, As=As, values=values, C=C)
            
    return value


def Rcomp_multiply_upper_topology(A, a, B, b, C):
    """ 
        Multiplication, extended for top, such that the upper topology
        is respected. 
        
        So 0 * Top = 0.
        and x * Top = Top.
    
    """
    a_is_top = is_top(A, a)
    b_is_top = is_top(B, b)
    a_is_zero = not a_is_top and a == 0.0
    b_is_zero = not b_is_top and b == 0.0
    
    # 0 * Top = 0
    if b_is_top:
        if a_is_zero:
            return 0.0
        else:
            return C.get_top()
    elif a_is_top:
        if b_is_zero:
            return 0.0
        else:
            return C.get_top()
    else:
        assert isinstance(a, float) 
        assert isinstance(b, float)
        
        # XXX: overflow
        try:
            return a * b
        except FloatingPointError as e:
            if 'underflow' in str(e):
                mcdp_dev_warning('Not sure about this.')
                return finfo.tiny 
            elif 'overflow' in str(e):
                return C.get_top()
            else:
                raise
                
#         
#         # first, find out if there are any tops
#         def is_there_a_top():
#             for Fi, fi in zip(self.F, f):
#                 if is_top(Fi, fi):
#                     return True
#             return False
#         
#         if is_there_a_top():
#             return self.R.get_top()
# 
#         mult = lambda x, y: x * y
#         try:
#             r = functools.reduce(mult, f)
#             if np.isinf(r):
#                 r = self.R.get_top()
#         except FloatingPointError as e:
#             # assuming this is overflow
#             if 'overflow' in str(e):
#                 r = self.R.get_top()
#             elif 'underflow' in str(e):
#                 r = finfo.tiny
#             else:
#                 raise
#         return r
    
                
