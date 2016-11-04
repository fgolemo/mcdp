# -*- coding: utf-8 -*-
from abc import abstractmethod

from contracts.utils import check_isinstance
from mcdp_posets import Map, Rcomp, RcompUnits, Nat
from mcdp_posets.nat import Nat_mult_lowersets_continuous
from mcdp_posets.poset import is_top
from mcdp_posets.rcomp import finfo
import numpy as np


__all__ = [
    'CeilMap', 
    'FloorMap', 
    'SquareMap', 
    'SqrtMap', 
    'SquareNatMap',
]


class GenericFloatOperation(Map):
    """ 
        Applies a function to a float and rounds it to the next integer,
        maintaining the float representation. 
        
        Can be used for Rcomp or Rcompunits.
    """

    def __init__(self, dom, name):
        assert isinstance(dom, (Rcomp, RcompUnits))
        Map.__init__(self, dom, dom)
        self.name = name

    def _call(self, x):
        if is_top(self.dom, x):
            return self.cod.get_top()
        
        if np.isinf(x):
            return self.cod.get_top()

        y = self.op(x)
        if np.isinf(y):
            return self.cod.get_top()

        return y
    
    def diagram_label(self):
        return self.name
    
    def repr_map(self, letter):
        return '%s ⟼ %s(%s)' % (letter, self.name, letter)

    @abstractmethod
    def op(self, x):
        pass
    
    def __repr__(self):
        return '%s(%s->%s)' % (self.name, self.dom, self.cod)
    
    
class CeilMap(GenericFloatOperation):
    """ 
        Applies a function to a float and rounds it to the next integer,
        maintaining the float representation. 
        
        Can be used for Rcomp or Rcompunits.
    """

    def __init__(self, dom):
        GenericFloatOperation.__init__(self, dom, 'ceil')

    def op(self, x):
        return np.ceil(x)


class Floor0Map(GenericFloatOperation):
    """
        This is floor0:
        
        floor0(f) = { 0 for f = 0
                      ceil(f-1) for f > 0    
    """
    
    def __init__(self, dom):
        GenericFloatOperation.__init__(self, dom, 'floor0')

    def op(self, x):
        if x == 0.0:
            return 0.0
        else:
            return np.ceil(x-1)
    
    
class FloorMap(GenericFloatOperation):

    def __init__(self, dom):
        GenericFloatOperation.__init__(self, dom, 'floor')

    def op(self, x):
                
        def square(x):
            try:
                res = x * x
            except FloatingPointError as e:
                if 'underflow' in str(e):
                    return finfo.tiny
                elif 'overflow' in str(e):
                    return finfo.max
                else:
                    raise
            return res

        return np.floor(x)
    
    
class SquareMap(GenericFloatOperation):

    def __init__(self, dom):
        GenericFloatOperation.__init__(self, dom, 'square')

    def op(self, x):
        return square(x)
    
    
class Linear1Map(GenericFloatOperation):
    """
        Computes y = a * x.
    """
    def __init__(self, dom, a):
        check_isinstance(dom, (Rcomp, RcompUnits))
        GenericFloatOperation.__init__(self, dom, 'linear1')
        self.a = a
 
    def op(self, x):
        assert isinstance(x, float) and x >= 0, x
        if np.isinf(x):
            return float('inf')
        try:
            res = x * self.a
            return res
        except FloatingPointError as e:
            s = str(e)
            if 'overflow' in s:
                return finfo.max
            elif 'underflow' in s:
                return finfo.tiny
            else:
                raise

class SquareNatMap(Map):

    def __init__(self):
        dom = Nat()
        cod = dom
        Map.__init__(self, dom, cod)

    def _call(self, x):
        return Nat_mult_lowersets_continuous(x, x)
    
    def repr_map(self, letter):
        return '%s ⟼ %s^2' % (letter, letter)



class SqrtMap(GenericFloatOperation):

    def __init__(self, dom):
        GenericFloatOperation.__init__(self, dom, 'sqrt')

    def op(self, x):
        return np.sqrt(x)
