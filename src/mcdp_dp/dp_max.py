# -*- coding: utf-8 -*-
from contracts.utils import raise_wrapped
from mcdp_maps import JoinNMap, Max1Map, MeetNMap
from mcdp_maps.max1map import Max1dualMap
from mcdp_posets import MapNotDefinedHere, Poset, PosetProduct, NotBounded
from mcdp_posets.poset import is_top, is_bottom
from mocdp.exceptions import mcdp_dev_warning

from .dp_flatten import MuxMap
from .dp_generic_unary import WrapAMap
from .primitive import EmptyDP


__all__ = [
    'Max1', # odd one out
    
    'JoinNDP',
    'MeetNDualDP',
    'MeetNDP',
    'JoinNDualDP',
]


class Max1(WrapAMap):
    """
        Join on a poset.  

        f ⟼ { max(value, f) }
        r ⟼  {r} if r >= value
               \emptyset otherwise 
    """
    def __init__(self, F, value):
        assert isinstance(F, Poset)
        m = Max1Map(F, value)
        md = Max1dualMap(R=F, value=value)
        WrapAMap.__init__(self, m, md)
        self.value = value
    
    def __repr__(self):
        return 'Max1(%r, %s)' % (self.F, self.value)

        
class MeetNDP(WrapAMap):
    """ 
        Meet (min) on a poset.  
        
        ⟨f₁, f₂, …⟩ ⟼ { min(f₁, f₂, …) }
        { ⟨r, ⊤, ⊤, … ⟩, ⟨⊤, r, ⊤, …⟩ } <-| r
    """

    def __init__(self, n, F):  #
        assert isinstance(F, Poset)
        h = MeetNMap(n, F)
        WrapAMap.__init__(self, h)
        self.F0 = F
        try:
            self.Rtop = self.R.get_top()
        except NotBounded as e:
            msg = 'MeetNDP requires that R has a top.'
            raise_wrapped(ValueError, e, msg, P=F) 
            
        self.n = n
        
    def solve_r(self, r):
        Rtop = self.Rtop
        n = self.n
        
        if is_top(self.R, r):
            return self.F.L(self.F.get_top())
        elif is_bottom(self.R, r):
            return self.F.L(self.F.get_bottom())
        else:
            maximals = set()
            for i in range(n):
                tops = [Rtop] * n
                tops[i] = r
                maximals.add(tuple(tops))
            return self.F.Ls(maximals)

    def diagram_label(self):  # XXX
        return 'Min'
    
    def __repr__(self):
        return 'MeetNDP(%s,%r)' % (self.n, self.F0)
    
        

class JoinNDP(WrapAMap):
    """ 
        Join ("max") of n variables.
        
        ⟨f₁, …, fₙ⟩ ⟼ { max(f₁, …, fₙ⟩ }
        r ⟼ ⟨r, …, r⟩
    """
    def __init__(self, n, P):
        h = JoinNMap(n, P)
        hd = MuxMap(P, [()] * n)
        WrapAMap.__init__(self, h, hd)

class JoinNDualDP(EmptyDP):
    """ 
        f ⟼ { ⟨f, ⊥, ⊥, ...⟩, ⟨⊥, f, ⊥, ⊥, ...⟩,  ... }
        ⟨r₁, …, rₙ⟩  ⟼ { max(r₁, …, rₙ) }
    """
    def __init__(self, n, P):
        F = P
        R = PosetProduct((P,)*n)
        EmptyDP.__init__(self, F=F, R=R)
        
        try:
            self.Fbot = F.get_bottom()
        except NotBounded as e:
            msg = 'JoinNDualDP requires that F has a bottom.'
            raise_wrapped(ValueError, e, msg, P=P) 
        self.n = n
        
        self.joinmap = JoinNMap(n, F)
        
    def solve_r(self, r):
        try:
            m = self.joinmap(r)
            return self.F.L(m)
        except MapNotDefinedHere:
            return self.F.Ls(set([]))
        
    def solve(self, f):
        n = self.n
        Fbot = self.Fbot
        
        if is_bottom(self.F, f):
            return self.R.U(self.R.get_bottom())
        elif is_top(self.F, f):
            return self.R.U(self.R.get_top())
        else:
            minimals = set()
            for i in range(n):
                tops = [Fbot] * n
                tops[i] = f
                minimals.add(tuple(tops))
            return self.R.Us(minimals)
         
mcdp_dev_warning('This screws up the optimization')
# class MeetNDualDP(Mux):
class MeetNDualDP(WrapAMap):
    """ 
    
        This is just a Mux 
    
        f ⟼ { ⟨f₁, f, ..., fₙ⟩ } 
        
        ⟨r₁, ..., rₙ⟩ ⟼ { min(r₁, ..., rₙ) }
        
    """
    def __init__(self, n, P):
        coords = [()] * n
        h = MuxMap(P, coords)
        hd = MeetNMap(n, P)
    
        WrapAMap.__init__(self, h, hd) 
        
        