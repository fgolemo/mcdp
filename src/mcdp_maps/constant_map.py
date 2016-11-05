# -*- coding: utf-8 -*-
from mcdp_posets import Map

__all__ = [
    'ConstantPosetMap',
]
 
class ConstantPosetMap(Map):
    """ 
        A map dom -> constant
    """

    def __init__(self, dom, cod, value):
        cod.belongs(value)
        Map.__init__(self, dom, cod)
        self.value = value

    def _call(self, x):  # @UnusedVariable
        return self.value
    
    def repr_map(self, letter):
        b = self.cod.format(self.value)
        return "%s ⟼ %s" % (letter, b)
