# -*- coding: utf-8 -*-
from mcdp_posets import Map, PosetProduct
from mocdp.exceptions import do_extra_checks


__all__ = [
    'ConstantMap',
]


class ConstantMap(Map):
    """ 
        A map 1 -> constant
    """

    def __init__(self, P, value):
        dom = PosetProduct(())
        cod = P
        Map.__init__(self, dom, cod)
        if do_extra_checks():
            P.belongs(value)
        
        self.value = value

    def _call(self, x):
        assert x == (), x
        return self.value 

