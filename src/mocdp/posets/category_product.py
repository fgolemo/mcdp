from contracts import contract
from abc import ABCMeta, abstractmethod
from mocdp.posets.space import Space, Map
from mocdp.posets.poset_product import PosetProduct

# 
# class GenericProduct():
#     
#     __metaclass__ = ABCMeta
#     
#     @contract(spaces='tuple($Space)')
#     def __init__(self, spaces):
#         self._spaces = spaces
# 
#     @abstractmethod
#     @contract(returns=Space)
#     def _get_space(self):
#         pass
#     
#     @abstractmethod
#     def pack(self, values):
#         """ Must return a value that belongs to Space """
#         
#     @abstract()
#     def unpack(self, packed):
#         """ Must return a value that belongs to Space """

# @contract(returns='tuple(Map, Map)', spaces='tuple, seq($Space)')
# def get_product1(spaces):
#
#     cod = []
#     indices = []
#
#     indices = get_flatten_muxmap()
#
#     for sub in spaces:
#         if isinstance(sub, PosetProduct):
#             for s in sub.subs:
#
#             cod.extend(sub.subs)
#         else:
#             cod.append(sub)
#
#
# class Pack(Map):
#     # (a,b), (c,d,e) |-> (a, b, c, d, e)
#
#     def __init__(self, spaces):
#         dom = PosetProduct(spaces)
#         cod = []
#     def _call(self, x):
#         pass
#
#
#
# if False:
#     # Huge product spaces
#     def prod_make(S1, S2):
#         S = PosetProduct((S1, S2))
#         return S
#
#     def prod_get_state(S1, S2, s):  # @UnusedVariable
#         (s1, s2) = s
#         return (s1, s2)
# else:
#
#     def prod_make(S1, S2):
#         assert isinstance(S1, PosetProduct), S1
#         if isinstance(S2, PosetProduct):
#             S = PosetProduct(S1.subs + S2.subs)
#         else:
#             S = PosetProduct(S1.subs + (S2,))
#
#         return S
#
#     def prod_make_state(S1, S2, s1, s2):
#         assert isinstance(S1, PosetProduct), S1
#         assert isinstance(s1, tuple)
#         if isinstance(S2, PosetProduct):
#             assert isinstance(s2, tuple)
#             return s1 + s2
#         else:
#             return s1 + (s2,)
#
#     def prod_get_state(S1, S2, s):
#         assert isinstance(S1, PosetProduct)
#         assert isinstance(s, tuple)
#         n1 = len(S1)
#
#         s1 = s[:n1]
#         s2 = s[n1:]
#         if isinstance(S2, PosetProduct):
#             pass
#         else:
#             assert len(s2) == 1
#             s2 = s2[0]
#
#         return (s1, s2)
