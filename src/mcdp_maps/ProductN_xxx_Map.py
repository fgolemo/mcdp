# -*- coding: utf-8 -*-
import functools

from contracts import contract
from contracts.utils import check_isinstance
from mcdp_posets import Map, PosetProduct, RcompUnits, is_top, Nat, Rcomp
from mcdp_posets.rcomp import finfo
from mocdp.exceptions import mcdp_dev_warning
import numpy as np


__all__ = [
    'ProductNMap',
    'ProductNNatMap',
]

class ProductNMap(Map):

    @contract(Fs='tuple[>=2]')
    def __init__(self, Fs, R):
        """ Should be all Rcomp or all RcompUnits """
        for _ in Fs:
            check_isinstance(_, (Rcomp, RcompUnits))
        check_isinstance(R, (Rcomp, RcompUnits))

        self.F = dom = PosetProduct(Fs)
        self.R = cod = R
        Map.__init__(self, dom=dom, cod=cod)

    def _call(self, f):
        
        # first, find out if there are any tops
        def is_there_a_top():
            for Fi, fi in zip(self.F, f):
                if is_top(Fi, fi):
                    return True
            return False
        
        if is_there_a_top():
            return self.R.get_top()

        mult = lambda x, y: x * y
        try:
            r = functools.reduce(mult, f)
            if np.isinf(r):
                r = self.R.get_top()
        except FloatingPointError as e:
            # assuming this is overflow
            if 'overflow' in str(e):
                r = self.R.get_top()
            elif 'underflow' in str(e):
                r = finfo.tiny
            else:
                raise
        return r
    

class ProductNNatMap(Map):

    """ Multiplies several Nats together """

    @contract(n='int,>=2')
    def __init__(self, n):
        self.P = Nat()
        dom = PosetProduct( (self.P,) * n)
        cod = self.P
        Map.__init__(self, dom=dom, cod=cod)
        self.n = n
                     
    def _call(self, x):
        def is_there_a_top():
            for xi in x:
                if self.P.equal(self.P.get_top(), xi):
                    return True
            return False

        # XXX: this is also wrong, possibly
        if is_there_a_top():
            return self.P.get_top()
        
        mult = lambda a, b : a * b
        r = functools.reduce(mult, x)
        mcdp_dev_warning('lacks overflow')
        return r

    def __repr__(self):
        return 'ProductNatN(%s)' % (self.n)