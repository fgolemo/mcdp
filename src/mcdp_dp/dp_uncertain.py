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

    def solve_r(self, func):
        raise NotSolvableNeedsApprox(type(self))

    def evaluate(self, m):
        raise NotSolvableNeedsApprox(type(self))

    def __repr__(self):
        return 'UncertainGate(%r)' % self.F0

    def get_lower_bound(self, n):  # @UnusedVariable
        return UncertainGateL(self.F0)
#         m1 = CheckOrder(self.F0)
#         m2 = MuxMap(self.F, coords=0)
#         dp = WrapAMap(MapComposition((m1, m2)))
#         return dp

    def get_upper_bound(self, n):  # @UnusedVariable
        return UncertainGateU(self.F0)
#         m1 = CheckOrder(self.F0)
#         m2 = MuxMap(self.F, coords=1)
#         dp = WrapAMap(MapComposition((m1, m2)))
#         return dp
    
class UncertainGateU(WrapAMap):
    """
        h  :〈f1, f2〉⟼ {f2}
        h* : f2 ⟼ {〈⊤, f2〉}
    """
    def __init__(self, F0):
        F = PosetProduct((F0, F0))
        m1 = CheckOrder(F0)
        m2 = MuxMap(F, coords=1) # extract second coordinate
        h = MapComposition((m1, m2))
        hd = FirstTop(F0) 
        WrapAMap.__init__(self, h, hd)


class UncertainGateL(WrapAMap):
    """
        h  :〈f1, f2〉⟼ {f1}
        h* : f1 ⟼ {〈f1, ⊤〉}     (SecondTop)
    """
    def __init__(self, F0):
        F = PosetProduct((F0, F0))
        m1 = CheckOrder(F0)
        m2 = MuxMap(F, coords=0) # extract second coordinate
        h = MapComposition((m1, m2))
        hd = SecondTop(F0) 
        WrapAMap.__init__(self, h, hd)
        

class SecondTop(Map):
    """
        x ⟼〈x, ⊤〉
    """
    
    def __init__(self, P):
        cod = PosetProduct((P, P))
        Map.__init__(self, dom=P, cod=cod)
        self.top = P.get_top()
    
    def _call(self, x):
        return (x, self.top)

class FirstTop(Map):
    """
        x ⟼〈⊤, x〉
    """
    
    def __init__(self, P):
        cod = PosetProduct((P, P))
        Map.__init__(self, dom=P, cod=cod)
        self.top = P.get_top()
    
    def _call(self, x):
        return (self.top, x)
    
# class LMap(Map):
#     """
#         f ⟼〈⊥, f〉
#     """
#     def __init__(self, F):
#         F2 = PosetProduct((F, F))
#         Map.__init__(self, dom=F, cod=F2)
#         self.bottom = F.get_bottom()
#         
#     def _call(self, x):
#         return (self.bottom, x)

    

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

    def repr_map(self, letter):
        return "⟨x1, x2⟩ ⟼ ⟨x1, x2⟩ (checks order)".replace('x', letter)

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

    def solve(self, f):
        raise NotSolvableNeedsApprox(type(self))

    def solve_r(self, r):
        raise NotSolvableNeedsApprox(type(self))

    def __repr__(self):
        return 'UncertainGateSym(%r)' % self.F0

    def get_lower_bound(self, n):  # @UnusedVariable
        return LMapDP(self.F)

    def get_upper_bound(self, n):  # @UnusedVariable
        return UMapDP(self.F)


class UMapDP(WrapAMap):
    """
        r = ⟨r₁, r₂⟩
        
        f ≤ r₁
        
        f ⟼〈f, ⊥〉
        ⟨r₁, r₂⟩ ⟼ r₁ 
        
    """
    def __init__(self, F):
        amap = UMap(F)
        F2 = PosetProduct((F, F))
        amap_dual = MuxMap(F2, 0)
        WrapAMap.__init__(self, amap, amap_dual)

class LMapDP(WrapAMap):
    """
        r = ⟨r₁, r₂⟩
        
        f ≤ r2
        
        f ⟼〈⊥, f 〉
        ⟨r₁, r₂⟩ ⟼ r₂ 
        
    """
    def __init__(self, F):
        amap = LMap(F)
        F2 = PosetProduct((F, F))
        amap_dual = MuxMap(F2, 1)
        WrapAMap.__init__(self, amap, amap_dual)


class UMap(Map):
    """
        f ⟼〈f, ⊥〉
    """
    
    def __init__(self, F):
        F2 = PosetProduct((F, F))
        Map.__init__(self, dom=F, cod=F2)
        self.bottom = F.get_bottom()
    
    def _call(self, x):
        return (x, self.bottom)

class LMap(Map):
    """
        f ⟼〈⊥, f〉
    """
    def __init__(self, F):
        F2 = PosetProduct((F, F))
        Map.__init__(self, dom=F, cod=F2)
        self.bottom = F.get_bottom()
        
    def _call(self, x):
        return (self.bottom, x)
