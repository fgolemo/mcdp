from mcdp_posets.space import Map, MapNotDefinedHere
from contracts import contract
from mcdp_posets.poset import Poset, NotJoinable
from mcdp_posets.poset_product import PosetProduct
from contracts.utils import raise_wrapped

__all__ = [
    'MeetNMap',
]

# class MeetMap2(Map):
#
#     @contract(F=Poset)
#     def __init__(self, F):
#         assert isinstance(F, Poset), F
#         self.F = F
#         dom = PosetProduct((F, F))
#         cod = F
#         Map.__init__(self, dom=dom, cod=cod)
#
#     def _call(self, x):
#         assert isinstance(x, tuple) and len(x) == 2, x
#         f1, f2 = x
#         r = self.F0.meet(f1, f2)
#         return r


class MeetNMap(Map):
    """ 
    
        A map that computes the meet of n arguments. 
    
        Raises MapNotDefinedHere if the elements are not joinable.
    """

    @contract(n='int,>=1', P=Poset)
    def __init__(self, n, P):
        dom = PosetProduct((P,) * n)
        cod = P
        Map.__init__(self, dom, cod)
        self.P = P

    def _call(self, xs):
        try:
            res = xs[0]
            for x in xs[1:]:
                res = self.P.meet(res, x)
            return res
        except NotJoinable as e:
            msg = 'Cannot meet all elements.'
            raise_wrapped(MapNotDefinedHere, e, msg, res=res, x=x)
