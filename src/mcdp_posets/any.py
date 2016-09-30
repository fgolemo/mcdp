from contracts.utils import raise_wrapped

from .poset import NotLeq, Poset
from .space import NotEqual


__all__ = [
    'Any',
    'TopCompletion',
    'BottomCompletion',
]

class Any(Poset):
    """ 
        This represents the space of all Python objects
        with equality given by Python's == operator
        and trivial leq.  
    """

    def witness(self):
        return 0
    def belongs(self, x):
        pass  # true

    def check_equal(self, x, y):
        if not (x == y):
            msg = 'Not equal '
            raise NotEqual(msg)

    def check_leq(self, x, y):
        try:
            self.check_equal(x, y)
        except NotEqual as e:
            msg = 'Trivial.'
            raise_wrapped(NotLeq, e, msg)

    def __repr__(self):
        return 'Any()'

    def __eq__(self, other):
        # all objects of this class are the same
        return isinstance(other, Any)


class TopCompletion(Poset):
    def __init__(self, P):
        self.P = P
        self.top = 'TT'
        
    def get_top(self):
        return self.top
    
    def get_bottom(self):
        return self.P.get_bottom()

    def belongs(self, x):
        if x == self.top:
            return
        self.P.belongs(x)
        
    def check_equal(self, x, y):
        if x == self.top and y == self.top:
            return
        if x == self.top or y == self.top:
            msg = 'x %s != %s y' % (x, y)
            raise NotEqual(msg)
        self.P.check_equal(x, y)
    
    def check_leq(self, x, y):
        if y == self.top:
            return 
        if x == self.top:  # and y != top
            msg = 'top is always greater'
            raise NotLeq(msg)
        self.P.check_leq(x, y)
        
    def __repr__(self):
        return 'T%s' % self.P

    def __eq__(self, other):
        return isinstance(other, TopCompletion) and other.P == self.P
    
    def witness(self):
        return self.top

class BottomCompletion(Poset):
    def __init__(self, P):
        self.P = P
        self.bottom = 'BB'

    def witness(self):
        return self.bottom

    def get_bottom(self):
        return self.bottom

    def get_top(self):
        return self.P.get_top()

    def belongs(self, x):
        if x == self.bottom:
            return
        self.P.belongs(x)

    def check_equal(self, x, y):
        if x == self.bottom and y == self.bottom:
            return
        if x == self.bottom or y == self.bottom:
            msg = 'x %s != %s y' % (x, y)
            raise NotEqual(msg)
        self.P.check_equal(x, y)

    def check_leq(self, x, y):
        if x == self.bottom:
            return
        if y == self.bottom:  # and y != top
            msg = 'bottom is always least'
            raise NotLeq(msg)
        self.P.check_leq(x, y)

    def __repr__(self):
        return 'B%s' % self.P

    def __eq__(self, other):
        return isinstance(other, BottomCompletion) and other.P == self.P
