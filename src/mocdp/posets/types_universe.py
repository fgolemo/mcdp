from .nat import Int, Nat
from .poset import NotLeq, Preorder
from .rcomp import Rcomp
from .space import Map, NotBelongs, NotEqual, Space
from .space_product import SpaceProduct
from contracts import contract
from contracts.utils import raise_desc, raise_wrapped
from mocdp.exceptions import DPInternalError, mcdp_dev_warning
import numpy as np

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

    def belongs(self, x):
        from mocdp.posets.rcomp_units import RcompUnits
        known = (RcompUnits, Rcomp)
        if not isinstance(x, known):
            raise_desc(NotBelongs, x=x, known=known)

    def check_equal(self, A, B):
        if not(A == B):
            msg = 'Different by direct comparison.'
            raise_desc(NotEqual, msg, A=A, B=B)

    def check_leq(self, A, B):
        from mocdp.posets.finite_set import FiniteCollectionsInclusion
        from mocdp.posets.rcomp_units import RcompUnits

        if isinstance(A, Nat) and isinstance(B, Nat):
            return

        if isinstance(A, Nat) and isinstance(B, Int):
            return

        if isinstance(A, Int) and isinstance(B, Int):
            return
        
        # Natural numbers can be embdedded into reals
        # (well, not all natural numbers, not biglongs, but close enough)
#         if isinstance(A, Nat) and isinstance(B, RcompUnits):
#             return
        if isinstance(A, Nat) and isinstance(B, Rcomp):
            return

        if isinstance(A, FiniteCollectionsInclusion) and isinstance(B, FiniteCollectionsInclusion):
            self.check_leq(A.S, B.S)
            return
        
        if isinstance(A, RcompUnits) and isinstance(B, RcompUnits):
            if A.units.dimensionality == B.units.dimensionality:
                return
            else:
                msg = "Dimensionality do not match."
                raise_desc(NotLeq, msg,
                           A_dimensionality=A.units.dimensionality,
                           B_dimensionality=B.units.dimensionality)

        if isinstance(A, Rcomp) and isinstance(B, RcompUnits): 
            return

        if isinstance(B, Rcomp) and isinstance(A, RcompUnits):
            return

        from mocdp.posets.uppersets import UpperSets
        if isinstance(A, UpperSets) and isinstance(B, UpperSets):
            self.check_leq(A.P, B.P)
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
            raise_wrapped(DPInternalError, e, msg, compact=True)

        from mocdp.posets.rcomp_units import RcompUnits
        from mocdp.posets.rcomp_units import format_pint_unit_short
        from mocdp.posets.maps.identity import IdentityMap


        if isinstance(A, Nat) and isinstance(B, Rcomp):
            return PromoteToFloat(A, B), CoerceToInt(B, A)

        if isinstance(A, Nat) and isinstance(B, Int):
            return IdentityMap(A, B), IdentityMap(B, A)
            
        if isinstance(A, RcompUnits) and isinstance(B, RcompUnits):
            assert A.units.dimensionality == B.units.dimensionality

            factor = float(B.units / A.units)
            B_to_A = LinearMapComp(B, A, factor)
            A_to_B = LinearMapComp(A, B, 1.0 / factor)

            a = format_pint_unit_short(A.units)
            b = format_pint_unit_short(B.units)
            setattr(B_to_A, '__name__', '%s-to-%s' % (b, a))
            setattr(A_to_B, '__name__', '%s-to-%s' % (a, b))
            return A_to_B, B_to_A


        if self.equal(A, B):
            return IdentityMap(A, B), IdentityMap(B, A)

        if isinstance(A, Rcomp) and isinstance(B, RcompUnits):
            return IdentityMap(A, B), IdentityMap(B, A)

        if isinstance(B, Rcomp) and isinstance(A, RcompUnits):
            return IdentityMap(A, B), IdentityMap(B, A)

        if isinstance(A, SpaceProduct) and isinstance(B, SpaceProduct):
            return get_product_embedding(self, A, B)

        from mocdp.posets.uppersets import UpperSets
        if isinstance(A, UpperSets) and isinstance(B, UpperSets):
            P_A_to_B, P_B_to_A = self.get_embedding(A.P, B.P)
            m1 = LiftToUpperSets(P_A_to_B)
            m2 = LiftToUpperSets(P_B_to_A)
            setattr(m1, '__name__', 'L%s' % P_A_to_B.__name__)
            setattr(m1, '__name__', 'L%s' % P_B_to_A.__name__)
            return m1, m2

        from mocdp.posets.finite_set import FiniteCollectionsInclusion
        if isinstance(A, FiniteCollectionsInclusion) and isinstance(B, FiniteCollectionsInclusion):
            a_to_b, b_to_a = self.get_embedding(A.S, B.S)
            m1 = LiftToFiniteCollections(a_to_b)
            m2 = LiftToFiniteCollections(b_to_a)
            setattr(m1, '__name__', 'L%s' % a_to_b.__name__)
            setattr(m1, '__name__', 'L%s' % b_to_a.__name__)
            return m1, m2

        msg = 'Spaces are ordered, but you forgot to code embedding.'
        raise_desc(NotImplementedError, msg, A=A, B=B)

class LiftToUpperSets(Map):
    """ Lift the map f to uppersets """
    @contract(f=Map)
    def __init__(self, f):
        from mocdp.posets.uppersets import UpperSets
        dom = UpperSets(f.get_domain())
        cod = UpperSets(f.get_codomain())
        self.f = f
        Map.__init__(self, dom=dom, cod=cod)

    def _call(self, x):
        minimals = x.minimals
        elements2 = set(self.f(_) for _ in minimals)
        from mocdp.posets.uppersets import UpperSet
        return UpperSet(elements2, self.cod.P)


def express_value_in_isomorphic_space(S1, s1, S2):
    """ expresses s1 in S2 """
    A_to_B, _ = tu.get_embedding(S1, S2)
    return A_to_B(s1)


class LiftToFiniteCollections(Map):

    @contract(f=Map)
    def __init__(self, f):
        from mocdp.posets.finite_set import FiniteCollectionsInclusion
        dom = FiniteCollectionsInclusion(f.get_domain())
        cod = FiniteCollectionsInclusion(f.get_codomain())
        self.f = f
        Map.__init__(self, dom=dom, cod=cod)

    def _call(self, x):
        elements = x.elements
        elements2 = set(self.f(_) for _ in elements)
        from mocdp.posets.finite_set import FiniteCollection
        return FiniteCollection(elements2, self.cod)

class CoerceToInt(Map):

    @contract(cod=Space, dom=Space)
    def __init__(self, cod, dom):
        # todo: check dom is Nat or Int
        Map.__init__(self, cod, dom)

    def _call(self, x):
        return int(x)


class PromoteToFloat(Map):

    @contract(cod=Space, dom=Space)
    def __init__(self, cod, dom):
        # todo: check dom is Rcomp or Rcompunits
        Map.__init__(self, cod, dom)

    def _call(self, x):
        return float(x)


class ProductMap(Map):
    @contract(fs='seq[>=1]($Map)')
    def __init__(self, fs):
        fs = tuple(fs)
        self.fs = fs
        mcdp_dev_warning('add promotion to SpaceProduct')
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
            raise_wrapped(NotLeq, e, msg, compact=True, a=a, b=b)


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
