# -*- coding: utf-8 -*-
from contracts import contract
from contracts.utils import check_isinstance
from mcdp_posets import Map, Nat, RcompUnits, is_top
from mcdp_posets.nat import Nat_mult_uppersets_continuous, \
    Nat_mult_lowersets_continuous, RcompUnits_mult_lowersets_continuous
from mcdp_posets.rcomp import Rcomp_multiply_upper_topology
import numpy as np


__all__ = [
    'MultValueNatMap', 
    'MultValueMap',
    
    'InvMultDualValueNatMap',
    'InvMultValueNatMap',
]

class MultValueNatMap(Map):
    """ Multiplies using the upper set topology. """
    @contract(value=int)
    def __init__(self, value):
        self.value = value
        self.N = Nat()
        Map.__init__(self, dom=self.N, cod=self.N)

    def _call(self, x):
        return Nat_mult_uppersets_continuous(self.value, x) 

class InvMultDualValueNatMap(Map):
    """ Multiplies using the lower set topology. """
    @contract(value=int)
    def __init__(self, value):
        self.value = value
        dom = cod = Nat()
        Map.__init__(self, dom, cod)

    def _call(self, x):
        return Nat_mult_lowersets_continuous(self.value, x) 

class InvMultDualValueMap(Map):
    """ Multiplies using the lower set topology. """
    def __init__(self, dom, cod, space, value):
        space.belongs(value)
        self.value = value
        self.space = space
        Map.__init__(self, dom, cod)

    def _call(self, x):
        A,a  = self.dom,x
        B,b = self.space, self.value 
        C = self.cod
        return RcompUnits_mult_lowersets_continuous(A, a, B, b, C)

class InvMultValueNatMap(Map):
    """ x |-> 
             if x != top
                ceil(f/c) if c < Top
                {0} if c = Top
            if x == top:
                {0}
    """
    @contract(value=int)
    def __init__(self, value):
        self.value = value
        dom = cod = Nat()
        Map.__init__(self, dom, cod)

    def _call(self, x):
        if self.dom.leq(self.value, 0): # value == 0
            return self.cod.get_top()
        else:
            if is_top(self.dom, x):
                return self.cod.get_top()
            else:
                if is_top(self.dom, self.value):
                    return 0
                else:
                    assert self.value > 0
                    return int(np.ceil(float(x)/self.value))


class InvMultValueMap(Map):
    """ x |-> 
             if x != top
                ceil(f/c) if c < Top
                {0} if c = Top
            if x == top:
                {0}
    """
    
    def __init__(self, dom, cod, space, value):
        check_isinstance(dom, RcompUnits)
        check_isinstance(cod, RcompUnits)
        space.belongs(value)
        self.value = value
        self.space = space
        # XXX: not sure about the units
        # assert (dom * space = cod)
        Map.__init__(self, dom, cod)

    def _call(self, x):
        if self.dom.leq(self.value, 0.0): # value == 0
            return self.cod.get_top()
        else:
            if is_top(self.dom, x):
                return self.cod.get_top()
            else:
                if is_top(self.dom, self.value):
                    return 0.0
                else:
                    assert self.value > 0.0
                    return float(x) / self.value


class MultValueMap(Map):
    """ 
        Multiplies by <value>.
        Implements _ -> _ * x on RCompUnits with the upper topology
        constraint (⊤ * 0 = 0 * ⊤ = 0)
    """
    def __init__(self, F, R, unit, value):
        check_isinstance(unit, RcompUnits)
        check_isinstance(F, RcompUnits)
        check_isinstance(R, RcompUnits)
        dom = F
        cod = R
        self.value = value
        self.unit = unit
        Map.__init__(self, dom=dom, cod=cod)

    def diagram_label(self):
        from mcdp_posets.rcomp_units import format_pint_unit_short
        if is_top(self.unit, self.value):
            label = '× %s' % self.unit.format(self.value)
        else:
            assert isinstance(self.value, float)
            label = '× %.5f %s' % (self.value, format_pint_unit_short(self.unit.units))
        return label

    def _call(self, x):
        return Rcomp_multiply_upper_topology(self.dom, x, 
                                             self.unit, self.value, 
                                             self.cod)
        
        