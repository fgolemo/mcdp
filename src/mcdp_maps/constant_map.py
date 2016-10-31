# -*- coding: utf-8 -*-
from mcdp_posets import Map


__all__ = [
#     'ConstantMap',
    'ConstantPosetMap',
]

# 
# class ConstantMap(Map):
#     """ 
#         A map 1 -> constant
#     """
# 
#     def __init__(self, P, value):
#         dom = PosetProduct(())
#         cod = P
#         Map.__init__(self, dom, cod)
#         if do_extra_checks():
#             P.belongs(value)
#         
#         self.value = value
# 
#     def _call(self, x):
#         assert x == (), x
#         return self.value 


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
