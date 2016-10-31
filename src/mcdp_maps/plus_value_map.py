# -*- coding: utf-8 -*-
from contracts import contract
from contracts.utils import check_isinstance
from mcdp_maps.SumN_xxx_Map import sum_units
from mcdp_posets import (Map, RcompUnits, Nat,
    express_value_in_isomorphic_space, Rcomp, is_top)
from mcdp_posets.nat import Nat_add
from mcdp_posets.rcomp_units import rcomp_add


__all__ = [
    'PlusValueNatMap',
    'MinusValueNatMap',
    'PlusValueMap',
    'PlusValueRcompMap',
    'MinusValueRcompMap',
    'MinusValueMap',
]


class PlusValueMap(Map):
    """ 
        Implements _ -> _ + c  for RcompUnits
    
    """

    @contract(F=RcompUnits, R=RcompUnits)
    def __init__(self, F, c_value, c_space, R):
        c_space.belongs(c_value)

        check_isinstance(F, RcompUnits)
        check_isinstance(c_space, RcompUnits)
        Map.__init__(self, dom=F, cod=R)
        self.c_value = c_value
        self.c_space = c_space
        self.F = F
        self.R = R

    def __repr__(self):
        return "+ %s" % self.c_space.format(self.c_value)

    def _call(self, x):
        values = [self.c_value, x]
        Fs = [self.c_space, self.F]
        return sum_units(Fs, values, self.R)

class PlusValueRcompMap(Map):
    """ 
        Implements _ -> _ + c  for Rcomp.    
    """

    def __init__(self, c_value):
        dom = Rcomp()
        dom.belongs(c_value)
        cod = dom
        Map.__init__(self, dom=dom, cod=cod)
        self.c_value = c_value

    def __repr__(self):
        return "+ %s" % self.dom.format(self.c_value)

    def _call(self, x):
        return rcomp_add(x, self.c_value)

class MinusValueRcompMap(Map):
    """ 
        Implements _ -> _ - c  for Rcomp.    
    """

    def __init__(self, c_value):
        dom = Rcomp()
        dom.belongs(c_value)
        cod = dom
        Map.__init__(self, dom=dom, cod=cod)
        self.c = c_value
        
        self.top = dom.get_top()

    def __repr__(self):
        return "- %s" % self.dom.format(self.c)

    def _call(self, x):
        dom, cod = self.dom, self.cod 
        
        if is_top(dom, self.c):
            return 0.0 
        
        if dom.leq(x, self.c):
            return 0.0
        else:
            if is_top(dom, x):
                return cod.get_top()
            else:
                check_isinstance(x, float)
                res = x - self.c
                assert res >= 0
                return res
                
#     def _call2(self, x):
#         P = self.dom
#         
#         if is_top(self.dom, self.c):
#             #  r = 0 -> f empty
#             #  r = 1 -> f empty
#             #  r = Top -> f <= Top
#             if is_top(self.dom, x):
#                 return self.top
#             else:
#                 raise MapNotDefinedHere()
#             
#         if P.equal(x, self.c):
#             return 0.0
#         else:
#             if P.leq(x, self.c):
#                 msg = '%s < %s' % (P.format(x), P.format(self.c))
#                 raise MapNotDefinedHere(msg)
#             else:
#                 if is_top(P, x):
#                     return self.top
#                 else:
#                     check_isinstance(x, float)
#                     res = x - self.c
#                     assert res >= 0
#                     # todo: check underflow
#                     return res
                
class MinusValueMap(Map):
    """ 
         h:  f ⟼  max(0, r-c) if  c ≠ ⊤
                   0           if  c = ⊤  
        (with c a positive constant.) 
    """

    @contract(P=RcompUnits, c_space=RcompUnits)
    def __init__(self, P, c_value, c_space):
        c_space.belongs(c_value)
        check_isinstance(P, RcompUnits)
        check_isinstance(c_space, RcompUnits)
    
        Map.__init__(self, dom=P, cod=P)
        self.c_value = c_value
        self.c_space = c_space

        self.c = express_value_in_isomorphic_space(c_space, c_value, P)
        self.P = P
        self.top = P.get_top()

    def __str__(self):
        return "- %s" % self.c_space.format(self.c_value)

    def __repr__(self):
        return "MinusValueMap(%s)" % self.__str__()

    def _call(self, x):
        """
        
        otherwise:
        
            h*: r |->   0   if r < value:
                    r - value  if r >= value 
                    
             h:  f ⟼  max(0, r-c) if  c ≠ ⊤
                       0           if  c = ⊤  


    
        """
        dom, cod = self.dom, self.cod 
        
        if is_top(dom, self.c):
            return 0.0 
        
        if dom.leq(x, self.c):
            return 0.0
        else:
            if is_top(dom, x):
                return cod.get_top()
            else:
                check_isinstance(x, float)
                res = x - self.c
                assert res >= 0
                return res


class PlusValueNatMap(Map):

    def __init__(self, value):
        self.value = value
        self.N = Nat()
        self.N.belongs(value)
        Map.__init__(self, dom=self.N, cod=self.N)

    def _call(self, x):
        return Nat_add(x, self.value) 

    def __repr__(self):
        return '+ %s' % self.N.format(self.value)


class MinusValueNatMap(Map):
    
    """
        if value is Top:
        
            r |->   MapNotDefinedHere   if r != Top
                    Top  if r == Top  
        
        otherwise:
        
            r |->   MapNotDefinedHere   if r < value:
                    r - value  if r >= value 
        f - Top <= r 
    
    """
    @contract(value=int)
    def __init__(self, value):
        self.c = value
        N = Nat()
        Map.__init__(self, dom=N, cod=N)
        self.top  = self.dom.get_top()
        
    def _call(self, x):
        dom, cod = self.dom, self.cod 
        
        if is_top(dom, self.c):
            return 0 
        
        if dom.leq(x, self.c):
            return 0
        else:
            if is_top(dom, x):
                return cod.get_top()
            else:
                check_isinstance(x, int)
                res = x - self.c
                assert res >= 0
                return res
            
#         P = self.dom
#         
#         if is_top(self.dom, self.c):
#             #  r = 0 -> f empty
#             #  r = 1 -> f empty
#             #  r = Top -> f <= Top
#             if is_top(self.dom, x):
#                 return self.top
#             else:
#                 raise MapNotDefinedHere()
#         
#         if P.equal(x, self.c):
#             return 0
#         else:
#             if P.leq(x, self.c):
#                 msg = '%s < %s' % (P.format(x), P.format(self.c))
#                 raise MapNotDefinedHere(msg)
#             else:
#                 if is_top(P, x):
#                     return self.top
#                 else:
#                     check_isinstance(x, int)
#                     res = x - self.c
#                     assert res >= 0
#                     # todo: check underflow
#                     return res
                
    def __repr__(self):
        return '- %s' % self.c