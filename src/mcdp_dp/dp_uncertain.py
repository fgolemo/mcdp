# -*- coding: utf-8 -*-
from .dp_flatten import MuxMap
from .dp_generic_unary import WrapAMap
from .primitive import ApproximableDP
from contracts import contract
from contracts.utils import raise_wrapped
from mcdp_dp import PrimitiveDP
from mcdp_maps import MapComposition
from mcdp_posets import PosetProduct, Space
from mcdp_posets.poset import NotLeq
from mcdp_posets.space import Map
from mocdp.exceptions import DPSemanticError
from mcdp_dp.primitive import NotSolvableNeedsApprox


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
        M = PosetProduct(())
        PrimitiveDP.__init__(self, F=F, R=R, M=M)

    def solve(self, func):
        raise NotSolvableNeedsApprox(type(self))

    def __repr__(self):
        return 'UncertainGate(%r)' % self.F0

    def get_lower_bound(self, n):  # @UnusedVariable
        m1 = CheckOrder(self.F0)
        m2 = MuxMap(self.F, coords=0)
        return WrapAMap(MapComposition((m1, m2)))

    def get_upper_bound(self, n):  # @UnusedVariable
        m1 = CheckOrder(self.F0)
        m2 = MuxMap(self.F, coords=1)
        return WrapAMap(MapComposition((m1, m2)))

class CheckOrder(Map):
    def __init__(self, F0):
        self.F0 = F0
        F = PosetProduct((F0, F0))
        Map.__init__(self, dom=F, cod=F0)
    def _call(self, x):
        l, u = x
        try:
            self.F0.check_leq(l, u)
        except NotLeq as e:
            msg = 'Run-time check failed; wrong use of "Uncertain" operator.'
            raise_wrapped(DPSemanticError, e, msg, l=l, u=u, compact=True)
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
        M = PosetProduct(())
        PrimitiveDP.__init__(self, F=F, R=R, M=M)

    def solve(self, func):
        raise NotSolvableNeedsApprox(type(self))

    def __repr__(self):
        return 'UncertainGateSym(%r)' % self.F0

    def get_lower_bound(self, n):  # @UnusedVariable
        return WrapAMap(LMap(self.F))

    def get_upper_bound(self, n):  # @UnusedVariable
        return WrapAMap(UMap(self.F))


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
