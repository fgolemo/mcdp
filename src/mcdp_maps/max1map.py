# -*- coding: utf-8 -*-
from contracts.utils import raise_wrapped, raise_desc
from mcdp_posets import Map, MapNotDefinedHere, NotJoinable
from mocdp.exceptions import do_extra_checks


__all__ = [
    'Max1Map',
    'Min1Map',
]

class Max1Map(Map):
    """
        f -> max(value, f)
    """
    def __init__(self, F, value):
        if do_extra_checks():
            F.belongs(value)

        Map.__init__(self, F, F)
        self.value = value
        self.F = F

    def _call(self, x):
        try:
            r = self.F.join(x, self.value)
        except NotJoinable as e:
            msg = 'Cannot compute join of elements.'
            raise_wrapped(MapNotDefinedHere, e, msg, value=self.value, x=x)
        return r
    
    def repr_map(self, letter):
        return "%s ⟼ %s ∧ %s" % (letter, letter, self.F.format(self.value))

class Min1Map(Map):
    """
        f -> min(value, f)
    """
    def __init__(self, F, value):
        if do_extra_checks():
            F.belongs(value)

        Map.__init__(self, F, F)
        self.value = value
        self.F = F

    def _call(self, x):
        try:
            r = self.F.meet(x, self.value)
        except NotJoinable as e:
            msg = 'Cannot compute meet of elements.'
            raise_wrapped(MapNotDefinedHere, e, msg, value=self.value, x=x)
        return r
    
    def repr_map(self, letter):
        return "%s ⟼ %s v %s" % (letter, letter, self.F.format(self.value))
  
class Min1dualMap(Map):
    """
  r ⟼ { {r} if r <= value
               ⊤ otherwise }    
    """
    def __init__(self, R, value):
        if do_extra_checks():
            R.belongs(value)

        Map.__init__(self, R, R)
        self.value = value
        self.R = R

    def _call(self, r):
        if self.R.leq(r, self.value):
            return r
        else:
            return self.R.get_top()
        
    def repr_map(self, letter):
        return "r ⟼ r if r ≽ %s, else ⊤".replace('r', letter)
        
class Max1dualMap(Map):
    """
        r -> { r   if r >= value
               undefined  otherwise
    """
    def __init__(self, R, value):
        if do_extra_checks():
            R.belongs(value)

        Map.__init__(self, R, R)
        self.value = value
        self.R = R

    def _call(self, r):
        if self.R.leq(self.value, r):
            return r
        else:
            raise_desc(MapNotDefinedHere, 'unfeasible')