# -*- coding: utf-8 -*-
from contracts import contract
from mcdp_posets import Map
from mcdp.exceptions import mcdp_dev_warning


__all__  = [
    'MapComposition',
]

class MapComposition(Map):

    """ Composition of a series of maps """

    @contract(maps='seq($Map)')
    def __init__(self, maps):
        """ 
            maps = [f, g, h]
            === h o g o f
            
            They are in order of application.
        """
        self.maps = tuple(maps)
        from mcdp_posets.types_universe import get_types_universe

        tu = get_types_universe()
        for i in range(len(maps)-1):
            first = maps[i]
            second =maps[i+1]
            cod1 = first.get_codomain()
            dom2 = second.get_domain()
            tu.check_equal(cod1, dom2)

        mcdp_dev_warning('Check that the composition makes sense')
        dom = self.maps[0].get_domain()
        cod = self.maps[-1].get_codomain()
        Map.__init__(self, dom=dom, cod=cod)

    def _call(self, x):
        res = x
        for m in self.maps:
            # may raise MapNotDefinedHere
            res = m.__call__(res)
        return res

    def repr_map(self, letter):
        return '%s ⟼ m2(m1(%s))' % (letter, letter)