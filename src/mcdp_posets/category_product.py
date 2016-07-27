from .poset import Poset
from .poset_product import PosetProduct
from .space import Space  # @UnusedImport
from .space_product import SpaceProduct
from contracts import contract
from mocdp import ATTRIBUTE_NDP_RECURSIVE_NAME
from mocdp.exceptions import do_extra_checks

__all__ = [
    'get_product_compact',
]

@contract(returns='tuple($Space, *, *)')
def get_product_compact(*spaces):
    """
        S, pack, unpack = get_product_compact(S1, S2)
    """
#     names = set()
#     for s in spaces:
#         from mocdp.comp.recursive_name_labeling import get_names_used
#         names.update(get_names_used(s))

    S = _prod_make(spaces)

#     S_names = set(get_names_used(S))
#     for i, s in enumerate(spaces):
#         print('spaces[%d] =  %s' % (i, s.__repr__()))
#     print('S      =  %s' % S.__repr__())
#
#     if S_names != names:
#         msg = 'invalid'
#         raise_desc(ValueError, msg, spaces=spaces, S=S, names=names, S_names=S_names)


    def pack(*elements):
        return _prod_make_state(elements, spaces)
    def unpack(s):
        return _prod_get_state(s, spaces)
    return S, pack, unpack

def get_subs(x):
    if hasattr(x,  ATTRIBUTE_NDP_RECURSIVE_NAME):
        # do not break the spaces that have a name
        return (x,)
    if isinstance(x, SpaceProduct):
        return x.subs
    else:
        return (x,)

def _prod_make(spaces):

    subs = ()
    for space in spaces:
        subs = subs + get_subs(space)
#
#         print('space: %s %s %s' % (id(space), space.__repr__(),
#                                    getattr(space, ATTRIBUTE_NDP_RECURSIVE_NAME, '-')))

    if len(subs) == 1:
        return subs[0]

    if all(isinstance(x, Poset) for x in subs):
        S = PosetProduct(subs)
    else:
        S = SpaceProduct(subs)
#
#
#     for i, sub in enumerate(subs):
#         print('name of %r = %s' % (sub, getattr(sub, ATTRIBUTE_NDP_RECURSIVE_NAME, '-')))

#     print('found: %s %r' % (id(S), S.__repr__()))

    return S

def _prod_make_state(elements, spaces):
    assert isinstance(elements, tuple), elements
    assert isinstance(spaces, tuple), spaces

    def get_state(X, x):
        if hasattr(X, ATTRIBUTE_NDP_RECURSIVE_NAME):
            # do not break the spaces that have a name
            return (x,)
        if isinstance(X, SpaceProduct):
            return x
        else:
            return (x,)

    s = ()
    for space, e in zip(spaces, elements):
        if do_extra_checks():
            space.belongs(e)
        s = s + get_state(space, e)

    if len(s) == 1:
        return s[0]

    return s

def _prod_get_state(s, spaces):
    subs = ()
    for space in spaces:
        subs = subs + get_subs(space)

    is_empty = len(subs) == 1
    if is_empty:
        s = (s,)

    # print('s: %s spaces: %s' % (s, spaces))
    assert isinstance(s, tuple)

    res = []
    for Si in spaces:
        if isinstance(Si, SpaceProduct):
            n = len(Si)
            si = s[:n]
            s = s[n:]
        else:
            si = s[0]
            s = s[1:]
        res.append(si)

    return tuple(res)

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
