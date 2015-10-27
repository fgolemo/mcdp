from contracts.utils import raise_desc, raise_wrapped
from mocdp.posets.poset import NotLeq, Preorder
from mocdp.posets.space import Map, NotEqual, Space
import numpy as np
from mocdp.posets.rcomp import Rcomp
from mocdp.posets.space_product import SpaceProduct
from contracts import contract
import warnings

__all__ = [
    'get_types_universe',
]



class TypesUniverse(Preorder):
    """
        In this pre-order, a type A <= B if we can find 
        and embedding of A in B. An embedding is a pair of functions
        f: A -> B and g: B -> A such that g(f(x)) = x.
        
        For example,  int <= float, and embedding = (float(), int())
    
    """

    def check_equal(self, A, B):
        if not(A == B):
            msg = 'Different by direct comparison.'
            raise_desc(NotEqual, msg, A=A, B=B)

    def check_leq(self, A, B):
        from mocdp.posets.rcomp_units import RcompUnits
        if isinstance(A, RcompUnits) and isinstance(B, RcompUnits):
            if A.units.dimensionality == B.units.dimensionality:
                return
            else:
                msg = "Dimensionality do not match."
                raise_desc(NotLeq, msg, A=A, B=B)

        if isinstance(A, Rcomp) and isinstance(B, RcompUnits): 
            return
        if isinstance(B, Rcomp) and isinstance(A, RcompUnits):
            return
        
        if isinstance(A, SpaceProduct) and isinstance(B, SpaceProduct):
            return check_leq_products(self, A, B)

        msg = "Do not know how to compare types."
        raise_desc(NotLeq, msg, A=A, B=B)
            

    def get_embedding(self, A, B):
        try:
            self.check_leq(A, B)
        except NotLeq as e:
            msg = 'Cannot get embedding if not preorder holds.'
            raise_wrapped(ValueError, e, msg)

        from mocdp.posets.rcomp_units import RcompUnits
        from mocdp.posets.rcomp_units import format_pint_unit_short

        if isinstance(A, RcompUnits) and isinstance(B, RcompUnits):
            assert A.units.dimensionality == B.units.dimensionality

            factor = float(B.units / A.units)
            B_to_A = LinearMapComp(B, A, factor)
            A_to_B = LinearMapComp(A, B, 1.0 / factor)

            a = format_pint_unit_short(A.units)
            b = format_pint_unit_short(B.units)
#             setattr(B_to_A, '__name__', '%s-to-%s-f%.3f' % (b, a, B_to_A.factor))
#             setattr(A_to_B, '__name__', '%s-to-%s-f%.3f' % (a, b, A_to_B.factor))
            setattr(B_to_A, '__name__', '%s-to-%s' % (b, a))
            setattr(A_to_B, '__name__', '%s-to-%s' % (a, b))
            return A_to_B, B_to_A


        if isinstance(A, Rcomp) and isinstance(B, RcompUnits):
            return Identity(A, B), Identity(B, A)
        if isinstance(B, Rcomp) and isinstance(A, RcompUnits):
            return Identity(A, B), Identity(B, A)

        if isinstance(A, SpaceProduct) and isinstance(B, SpaceProduct):
            return get_product_embedding(self, A, B)


        msg = 'Did not code embedding.'
        raise_desc(AssertionError, msg, A=A, B=B)

class Identity(Map):

    @contract(cod=Space, dom=Space)
    def __init__(self, cod, dom):
        Map.__init__(self, cod, dom)

    def _call(self, x):
        return x


class ProductMap(Map):
    @contract(fs='seq[>=1]($Map)')
    def __init__(self, fs):
        fs = tuple(fs)
        self.fs = fs
        warnings.warn('add promotion to SpaceProduct')
        dom = SpaceProduct(tuple(fi.get_domain() for fi in fs))
        cod = SpaceProduct(tuple(fi.get_codomain() for fi in fs))
        Map.__init__(self, dom=dom, cod=cod)

    def _call(self, x):
        x = tuple(x)
        return tuple(fi(xi) for fi, xi in zip(self.fs, x))

def get_product_embedding(tu, A, B):
    pairs = [tu.get_embedding(a, b) for a, b in zip(A, B)]
    fs = [x for x, _ in pairs]
    finv = [y for _, y in pairs]

    res = ProductMap(fs), ProductMap(finv)
    return res


def check_leq_products(tu, A, B):
    if len(A) != len(B):
        msg = 'Different length'
        raise_desc(NotLeq, msg, A=A, B=B)
    for a, b in zip(A, B):
        try:
            tu.check_leq(a, b)
        except NotLeq as e:
            msg = 'Found uncomparable elements'
            raise_wrapped(NotLeq, e, msg, a=a, b=b)


class LinearMapComp(Map):
    """ Linear multiplication on R + top """

    def __init__(self, A, B, factor):
        Map.__init__(self, A, B)
        self.A = A
        self.B = B
        self.factor = factor
    
    def _call(self, x):
        if self.A.equal(x, self.A.get_top()):
            return self.B.get_top()
        res = x * self.factor
        if np.isinf(res):
            return self.B.get_top()
        return res

tu = TypesUniverse()

def get_types_universe():
    return tu