# -*- coding: utf-8 -*-
from contracts import contract
from contracts.utils import check_isinstance, raise_wrapped
from mcdp_maps import (ConstantPosetMap, InvMultDualValueNatMap, MultValueMap,
                       MultValueNatMap, InvMultValueNatMap, InvMultValueMap, InvMultDualValueMap)
from mcdp_posets import Map, RcompUnits, is_top, Nat, Rcomp
from mcdp_posets.rcomp_units import inverse_of_unit, check_mult_units_consistency
import numpy as np

from .dp_generic_unary import WrapAMap


__all__ = [
    'MultValueDP',
    'MultValueNatDP',
    
    'InvMultValueNatDP',
    'InvMultValueRcompDP',
    'InvMultValueDP',
]

class MultValueDP(WrapAMap):
    """
        f ⋅ c ≤ r
        
        We have:
        
            f ⟼ f (⋅U) c
            
        where (⋅U) is the upper continuous extension of multiplication
        (if c = Top and f = 0, then Top * 0 = 0).

        So the corresponding hᵈ is:
        
            if c == 0:
            
                we have simply:
                
                r ⟼  Top
                      
            
            if c != Top:
                
                r ⟼ r (⋅U) c1    (or is it?)
                
                with c1 = 1 / c a number. 
                
                Note that we expect that if r = Top, 
            
            if c == Top:
            
                r |->   if r = 0, then f must be <= 0
                        if r > 0, then f <= 0 
                        if r = Top, then f <= Top
            
        
    From: The Cuntz semigroup and domain theory
        Klaus Keimel November 26, 2015

    There is no way to extend the multiplication to all of R+ in such a way 
    that it remains continuous for the interval topology. This fact had 
    been overlooked in [8] and had led to misleading statements in [8]. 
    If we extend multiplication by +∞ · 0 = 0 = 0 · (+∞), it remains continuous 
    for the upper topology, if we extend it by +∞ · 0 = +∞ = 0 · (+∞), 
    it remains continuous for the lower topology.

    """
    @contract(F=RcompUnits, R=RcompUnits, unit=RcompUnits)
    def __init__(self, F, R, unit, value):
        check_isinstance(F, RcompUnits)
        check_isinstance(R, RcompUnits)
        check_isinstance(unit, RcompUnits)
        
        try:
            check_mult_units_consistency(F, unit, R)
        except AssertionError as e:
            msg = 'Invalid units.'
            raise_wrapped(ValueError, e, msg, F=F, R=R, unit=unit)

        amap = MultValueMap(F=F, R=R, unit=unit, value=value)
        
        # if value = Top:
        #    f |-> f * Top 
        #     
        if is_top(unit, value):
            amap_dual = MultValueDPHelper2Map(R, F)
        elif unit.equal(0.0, value):
            amap_dual = ConstantPosetMap(R, F, F.get_top())
        else:    
            value2 = 1.0 / value
            unit2 = inverse_of_unit(unit)
            amap_dual = MultValueMap(F=R, R=F, unit=unit2, value=value2)
            
        WrapAMap.__init__(self, amap, amap_dual)

    def diagram_label(self):  
        return self.amap.diagram_label()

# 
# class MultValueDPHelper1Map(Map):
#     """
#         The case c == 0.
#         
#         Implements:
#                 r ->  Top if r = 0
#                       undefined if r >= 0 
#     """
#     def __init__(self, dom, cod):
#         Map.__init__(self, dom=dom, cod=cod)
#         
#     def _call(self, x):
#         # 0 |-> Top
#         if self.dom.equal(x, 0.0):
#             return self.cod.get_top()
#         # otherwise undefined
#         raise MapNotDefinedHere(x)
#     
#     def repr_map(self, letter):
#         return '%s ⟼ ⊤ if %s = 0, else ø' % (letter, letter)
        

class MultValueDPHelper2Map(Map):
    """
        Implements:
         r ⟼   if r = 0, then f must be <= 0
                 if r > 0, then f must be <= 0
                 if r = Top, then f <= Top
                 
    """
    def __init__(self, dom, cod):
        Map.__init__(self, dom=dom, cod=cod)
        
    def _call(self, x):
        if is_top(self.dom, x):
            return self.cod.get_top()
        else:
            return 0.0
        
    def repr_map(self, letter):
        return '%s ⟼ ⊤ if %s = ⊤, else 0' % (letter, letter)


class MultValueNatDPHelper2Map(Map):
    """
        Implements:
         r ⟼  if r = 0, then f must be <= 0
                 if r > 0, then f must be <= 0
                 if r = Top, then f <= Top
                 
    """
    def __init__(self):
        dom = cod = Nat()
        Map.__init__(self, dom=dom, cod=cod)
        
    def _call(self, x):
        if is_top(self.dom, x):
            return self.cod.get_top()
        else:
            return 0

    def repr_map(self, letter):
        return '%s ⟼ ⊤ if %s = ⊤, else 0' % (letter, letter)

        
class MultValueNatDP(WrapAMap):
    """

        f * c <= r 
    """
    
    def __init__(self, value):
        N = Nat()
        N.belongs(value)
        
        amap = MultValueNatMap(value)
        
        # if value = Top:
        #    f |-> f * Top 
        #     
        if is_top(N, value):
            amap_dual = MultValueNatDPHelper2Map()
        elif N.equal(0, value):
            # r |-> Top
            amap_dual = ConstantPosetMap(N, N, N.get_top())
        else:    
            # f * c <= r
            # f <= r / c
            # r |-> floor(r/c)
            amap_dual = MultValueNatDPhelper(value)
            
        WrapAMap.__init__(self, amap, amap_dual)
        
        
class MultValueNatDPhelper(Map):
    """  r ⟼ floor(r/c) """
    
    @contract(c='int')
    def __init__(self, c):
        check_isinstance(c, int)
        if c == 0:
            raise ValueError(c)
        cod = dom = Nat()
        Map.__init__(self, dom, cod)
        self.c = c
        
    def _call(self, r):
        if is_top(self.dom, r):
            return self.cod.get_top()
        else:
            fmax = int(np.floor( float(r) / self.c ))
            return fmax
        

class InvMultValueRcompDP(WrapAMap):
    def __init__(self, value):
        F = R = unit = Rcomp()
        unit.belongs(value)
        amap = InvMultValueMap(F, R, unit, value)
        amap_dual = InvMultDualValueMap(R, F, unit, value)            
        WrapAMap.__init__(self, amap, amap_dual)  
        
    def diagram_label(self):
        return self.amap.diagram_label()
    
    
class InvMultValueDP(WrapAMap):
    def __init__(self, F, R, unit, value):
        """ r * c >= f """ 
        if isinstance(F, RcompUnits):
            check_isinstance(R, RcompUnits)
            check_isinstance(unit, RcompUnits)
            try:
                check_mult_units_consistency(R, unit, F)
            except AssertionError as e:
                msg = 'Invalid units.'
                raise_wrapped(AssertionError, e, msg, F=F,R=R,unit=unit)
                
        else:
            check_isinstance(F, Rcomp)
            check_isinstance(R, Rcomp)
            check_isinstance(unit, Rcomp)
            
        unit.belongs(value)
        amap = InvMultValueMap(F, R, unit, value)
        amap_dual = InvMultDualValueMap(R, F, unit, value)    
        WrapAMap.__init__(self, amap, amap_dual)  
    
    def diagram_label(self):
        return self.amap.diagram_label()
    
    
class InvMultValueNatDP(WrapAMap):
    """
        f ≤ r * c
    """
    
    def __init__(self, value):
        N = Nat()
        N.belongs(value)
        
        amap = InvMultValueNatMap(value)
        amap_dual = InvMultDualValueNatMap(value)
            
        WrapAMap.__init__(self, amap, amap_dual)
        
    def diagram_label(self):
        return self.amap.diagram_label()
    