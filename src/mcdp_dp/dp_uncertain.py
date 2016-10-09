# -*- coding: utf-8 -*-
import copy

from contracts import contract
from contracts.utils import raise_wrapped
from mcdp_dp import NotSolvableNeedsApprox, PrimitiveDP, WrongUseOfUncertain
from mcdp_maps import MapComposition
from mcdp_posets import Map, NotLeq, PosetProduct, Space

from .dp_flatten import MuxMap
from .dp_generic_unary import WrapAMap
from .primitive import ApproximableDP


__all__ = [
    'UncertainGate',
    'UncertainGateSym',
]

class UncertainGate(ApproximableDP):
    """
    
        Fl -> |      |
        Fu -> | gate | -> F
    
    """
    @contract(F0=Space)
    def __init__(self, F0):
        self.F0 = F0
        F = PosetProduct((F0, F0))
        R = F0
        M = PosetProduct((F0, F0))  # must be same as approximations
        PrimitiveDP.__init__(self, F=F, R=R, I=M)

    def solve(self, func):
        raise NotSolvableNeedsApprox(type(self))

    def evaluate(self, m):
        raise NotSolvableNeedsApprox(type(self))

    def __repr__(self):
        return 'UncertainGate(%r)' % self.F0

    def get_lower_bound(self, n):  # @UnusedVariable
        m1 = CheckOrder(self.F0)
        m2 = MuxMap(self.F, coords=0)
        dp = WrapAMap(MapComposition((m1, m2)))
        # preserve_dp_attributes(self, dp)
        return dp

    def get_upper_bound(self, n):  # @UnusedVariable
        m1 = CheckOrder(self.F0)
        m2 = MuxMap(self.F, coords=1)
        dp = WrapAMap(MapComposition((m1, m2)))
        # preserve_dp_attributes(self, dp)
        return dp

class CheckOrder(Map):
    def __init__(self, F0):
        self.F0 = F0
        F = PosetProduct((F0, F0))
        Map.__init__(self, dom=F, cod=F)
    def _call(self, x):
        l, u = x
        try:
            self.F0.check_leq(l, u)
        except NotLeq as e:
            msg = 'Run-time check failed; wrong use of "Uncertain" operator.'
            raise_wrapped(WrongUseOfUncertain, e, msg, l=l, u=u, compact=True)
        return x


class UncertainGateSym(ApproximableDP):
    """
    
        F  -> |      | -> ? <= R1
              | gate | -> ? <= R2
              
        lower:
        
            (Bottom, f)
            (f, Bottom)
        
    """
    @contract(F0=Space)
    def __init__(self, F0):
        self.F0 = F0
        F = F0
        R = PosetProduct((F0, F0))
        I = copy.copy(F0)
        PrimitiveDP.__init__(self, F=F, R=R, I=I)

    def evaluate(self, m):
        raise NotSolvableNeedsApprox(type(self))

    def solve(self, func):
        raise NotSolvableNeedsApprox(type(self))

    def __repr__(self):
        return 'UncertainGateSym(%r)' % self.F0

    def get_lower_bound(self, n):  # @UnusedVariable
        dp = WrapAMap(LMap(self.F))
        return dp

    def get_upper_bound(self, n):  # @UnusedVariable
        dp = WrapAMap(UMap(self.F))
        return dp


class UMap(Map):
    def __init__(self, F):
        F2 = PosetProduct((F, F))
        Map.__init__(self, dom=F, cod=F2)
        self.bottom = F.get_bottom()
    def _call(self, x):
        return (x, self.bottom)

class LMap(Map):
    def __init__(self, F):
        F2 = PosetProduct((F, F))
        Map.__init__(self, dom=F, cod=F2)
        self.bottom = F.get_bottom()
    def _call(self, x):
        return (self.bottom, x)
