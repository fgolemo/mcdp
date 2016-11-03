# -*- coding: utf-8 -*-
from contracts.utils import check_isinstance
from mcdp_posets import RcompUnits, Rcomp
from mcdp_posets.rcomp_units import R_dimensionless

from .dp_misc_unary import CeilDP, Floor0DP
from .dp_multvalue import MultValueDP
from .dp_series_simplification import wrap_series


__all__ = [
    'makeLinearCeilDP',
    'makeLinearFloor0DP',
]

def makeLinearCeilDP(P, alpha):
    """
        Implements the approximation:
        
            y >= ( alpha * ceil(x) / alpha) )
    """
    if alpha <= 0:
        raise ValueError(alpha)
    
    alpha_inv = 1.0/alpha
    
    check_isinstance(P, (Rcomp, RcompUnits))
    
    if isinstance(P, Rcomp):
        dps = [
            MultValueDP(P, P, P, alpha_inv),
            CeilDP(P),
            MultValueDP(P, P, P, alpha),
        ]
        return wrap_series(P, dps)
    elif isinstance(P, RcompUnits):
        dimensionless = R_dimensionless
        dps = [
            MultValueDP(P, P, dimensionless, alpha_inv),
            CeilDP(P),
            MultValueDP(P, P, dimensionless, alpha),
        ]
        return wrap_series(P, dps)
    else:
        assert False, P

def makeLinearFloor0DP(P, alpha):
    """
        Implements the approximation:
        
            y >= ( alpha * floor0(x) / alpha) )
            
        where floor0 disagrees with floor on integers.
    """
    if alpha <= 0:
        raise ValueError(alpha)
    
    alpha_inv = 1.0/alpha
    
    check_isinstance(P, (Rcomp, RcompUnits))
    
    if isinstance(P, Rcomp):
        dps = [
            MultValueDP(P, P, P, alpha_inv),
            Floor0DP(P),
            MultValueDP(P, P, P, alpha),
        ]
        return wrap_series(P, dps)
    elif isinstance(P, RcompUnits):
        dimensionless = R_dimensionless
        dps = [
            MultValueDP(P, P, dimensionless, alpha_inv),
            Floor0DP(P),
            MultValueDP(P, P, dimensionless, alpha),
        ]
        return wrap_series(P, dps)
    else:
        assert False, P


# CombinedCeilDP
# class LinearCeil():
#     """
#      
#         y = ( alpha * ceil(x) / alpha) )
#          
#     """
#  
#  
#     def __init__(self, alpha):
#         self.alpha = alpha
#  
#     def __call__(self, x):
#         assert isinstance(x, float) and x >= 0, x
#         if math.isinf(x):
#             return float('inf')
#         if x == 0.0:
#             return 0.0
#  
#         try:
#             m = x / self.alpha
#         except FloatingPointError as e:
#             s = str(e)
#             if 'overflow' in s:
#                 m = finfo.max
#             elif 'underflow' in s:
#                 m = finfo.tiny
#             else:
#                 raise
#  
#         n = math.ceil(m)
#         y = n * self.alpha
#  
#         res = float(y)
#  
#         return res
#  
  
# class LogarithmicCeil():
#     """
#       
#         y = exp( alpha * ceil(log(x) / alpha) )
#           
#     """
#   
#     def __init__(self, alpha):
#         assert alpha > 0, alpha
#         self.alpha = alpha
#   
#     def __call__(self, x):
#         assert isinstance(x, float) and x >= 0, x
#         if math.isinf(x):
#             return float('inf')
#         if x == 0:
#             return 0.0
#         l = math.log10(x)
#         m = l / self.alpha
#         n = math.ceil(m)
#         o = n * self.alpha
#         y = math.pow(10, o)
#         return float(y)
     
# def identity(x):
#     return x
# 
# class CombinedCeilDP(WrapAMap):
#     
#     def __init__(self, S, alpha, step, max_value=None):
#         amap = CombinedCeilMap(S, alpha, step, max_value)
#         WrapAMap.__init__(self, amap)
#         
# class CombinedCeilMap(Map):
# 
#     def __init__(self, S, alpha, step, max_value=None):
#         Map.__init__(self, dom=S, cod=S)
#         self.max_value = max_value
# 
#         if alpha > 0:
#             self.f1 = LogarithmicCeil(alpha) 
#         else:
#             self.f1 = identity
#         
#         if step > 0:
#             self.f2 = LinearCeil(step)
#         else:
#             self.f2 = identity
# 
#         self.alpha = alpha
#         self.step = step
# 
#     def __repr__(self):
#         if self.alpha > 0:  # or self.max_value > 0:
#             mcdp_dev_warning('todo: self.max_value')
#             return ('CombinedCeil(alpha=%s, step=%s, max_value=%s)' %
#                     (self.alpha, self.step, self.max_value))
#         else:
#             return 'Discretize(%s)' % self.dom.format(self.step)
# 
#     def _call(self, x):
#         top = self.dom.get_top()
# 
#         if self.max_value is not None:
#             if not self.dom.leq(x, self.max_value):
#                 raise MapNotDefinedHere()
# 
#         if self.dom.equal(top, x):
#             return top
#         xx = self.f1(x)
#         y = self.f2(xx)
#         return y

# 
# class FloorStepMap(Map):
# 
#     def __init__(self, S, step):
#         check_isinstance(S, RcompUnits)
#         Map.__init__(self, dom=S, cod=S)
#         self.step = step
# 
#     def __repr__(self):
#         return 'FloorStep(%s)' % self.dom.format(self.step)
# 
#     def _call(self, x):
#         top = self.dom.get_top()
#         if self.dom.equal(top, x):
#             return top
# 
#         assert isinstance(x, float)
# 
#         try:
#             m = x / self.step
#         except FloatingPointError as e:
#             assert 'overflow' in str(e)
#             m = finfo.max
# 
#         n = math.floor(m)
#         y = n * self.step
#         return y
# 
# class FloorStepDP(WrapAMap):
#     def __init__(self, S, step):
#         amap = FloorStepMap(S, step)
#         WrapAMap.__init__(self, amap)
