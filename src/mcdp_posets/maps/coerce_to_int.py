# -*- coding: utf-8 -*-
import math

from contracts import contract
from contracts.utils import check_isinstance
from mcdp_posets import Map, Space
from mcdp_posets.nat import Nat
from mcdp_posets.poset import is_top
from mcdp_posets.rcomp import Rcomp
from mcdp_posets.rcomp_units import RcompUnits
from mcdp_posets.space import MapNotDefinedHere


__all__ = ['CoerceToInt']

class CoerceToInt(Map):

    """ 
        Coerces a float to integer. It is not defined in
        the case that the float is not rounded. 
    """  
    
    @contract(cod=Space, dom=Space)
    def __init__(self, dom, cod):
        check_isinstance(dom, (Rcomp, RcompUnits))
        check_isinstance(cod, Nat)

        Map.__init__(self, dom, cod)

    def _call(self, x):
        if is_top(self.dom, x):
            return self.cod.get_top()
        r = int(x)
        if r != x:
            msg = 'We cannot just coerce %r into an int.' % x
            raise MapNotDefinedHere(msg)
        return r
    
    def repr_map(self, letter):
        return "%s ⟼ (int) %s" % (letter, letter)
    
class FloorRNMap(Map):

    """ 
        From Rcomp to Nat. 

         x -> int(floor(x))
    """  
    
    @contract(cod=Space, dom=Space)
    def __init__(self, dom, cod):
        check_isinstance(dom, (Rcomp, RcompUnits))
        check_isinstance(cod, Nat)
        Map.__init__(self, dom, cod)

    def _call(self, x):
        if is_top(self.dom, x):
            return self.cod.get_top()
        assert isinstance(x, float)
        # XXX: overflow?
        r = int(math.floor(x))
        return r
    
    def repr_map(self, letter):
        return "%s ⟼ floor(%s)" % (letter, letter)

class CeilRNMap(Map):

    """ 
        From Rcomp to Nat. 
        
         x -> int(floor(x))
    """  
    
    @contract(cod=Space, dom=Space)
    def __init__(self, dom, cod):
        check_isinstance(dom, (Rcomp, RcompUnits))
        check_isinstance(cod, Nat)
        Map.__init__(self, dom, cod)

    def _call(self, x):
        if is_top(self.dom, x):
            return self.cod.get_top()
        assert isinstance(x, float)
        # XXX: overflow?
        r = int(math.ceil(x))
        return r
    
    def repr_map(self, letter):
        return "%s ⟼ floor(%s)" % (letter, letter)
