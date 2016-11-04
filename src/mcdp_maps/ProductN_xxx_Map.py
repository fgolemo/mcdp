# -*- coding: utf-8 -*-
from contracts import contract
from contracts.utils import check_isinstance
from mcdp_maps.repr_map import repr_map_product
from mcdp_posets import Map, PosetProduct, RcompUnits, Nat, Rcomp
from mcdp_posets.nat import Nat_mult_uppersets_continuous_seq
from mcdp_posets.rcomp import Rcomp_multiply_upper_topology_seq


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
        return Rcomp_multiply_upper_topology_seq(self.F.subs, f, self.R)

    def repr_map(self, letter):
        return repr_map_product(letter, len(self.F))


    

class ProductNNatMap(Map):

    """ Multiplies several Nats together. 
    
        0 * Top = 0  (Nat_mult_uppersets_continuous_seq)
    """

    @contract(n='int,>=2')
    def __init__(self, n):
        self.P = Nat()
        dom = PosetProduct( (self.P,) * n)
        cod = self.P
        Map.__init__(self, dom=dom, cod=cod)
        self.n = n
                     
    def _call(self, x):
        return Nat_mult_uppersets_continuous_seq(x)

    def __repr__(self):
        return 'ProductNNatMap(%s)' % (self.n)

    def repr_map(self, letter):
        return repr_map_product(letter, self.n)
