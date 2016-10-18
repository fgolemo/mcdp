# -*- coding: utf-8 -*-
from contracts import contract
from mcdp_posets import Map, PosetProduct, Rcomp
from mocdp.exceptions import mcdp_dev_warning


__all__ = ['SumNRcomp']

class SumNRcomp(Map):
    """ Sum of N Rcomps. """
    
    @contract(n='int,>=0')
    def __init__(self, n):
        P = Rcomp()
        dom = PosetProduct((P,)*n)
        cod = P
        Map.__init__(self, dom=dom, cod=cod)
    
    def _call(self, x):
        res = sum(x)
        mcdp_dev_warning('overflow, underflow')
        return res
