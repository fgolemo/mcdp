from .nat import Int, Nat
from .poset import NotLeq, Preorder
from .rcomp import Rcomp
from .space import NotBelongs, NotEqual
from .space_product import SpaceProduct
from contracts.utils import raise_desc, raise_wrapped
from mocdp.exceptions import DPInternalError

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
        from mcdp_posets.rcomp_units import RcompUnits
        known = (RcompUnits, Rcomp)
        if not isinstance(x, known):
            raise_desc(NotBelongs, x=x, known=known)

    def check_equal(self, A, B):
        from mcdp_posets.poset_product import PosetProduct
        if isinstance(A, PosetProduct) and isinstance(B, PosetProduct):
            if len(A) != len(B):
                msg = 'Different length.'
                raise_desc(NotEqual, msg, A=A, B=B)
            for i, (sa, sb) in enumerate(zip(A.subs, B.subs)):
                try:
                    self.check_equal(sa, sb)
                except NotEqual as e:
                    msg = 'Element %d not equal.' % i
                    raise_wrapped(NotEqual, e, msg)

        if not(A == B):
            msg = 'Different by direct comparison.'
            raise_desc(NotEqual, msg, A=A, B=B)


    def check_leq(self, A, B):
        from mcdp_posets import FiniteCollectionsInclusion
        from mcdp_posets import RcompUnits

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

        from mcdp_posets import UpperSets
        if isinstance(A, UpperSets) and isinstance(B, UpperSets):
            self.check_leq(A.P, B.P)
            return
        
        if isinstance(A, SpaceProduct) and isinstance(B, SpaceProduct):
            return check_leq_products(self, A, B)

        from mcdp_posets import FinitePoset
        if isinstance(A, FinitePoset) and isinstance(B, FinitePoset):
            # A <= B if
            # TODO: check inclusion
            if A.get_elements() == B.get_elements():
                # TODO: check relations!
                return True
            raise NotImplementedError
            return


        msg = "Do not know how to compare types."
        raise_desc(NotLeq, msg, A=A, B=B)
            

    def get_embedding(self, A, B):
        try:
            self.check_leq(A, B)
        except NotLeq as e:
            msg = 'Cannot get embedding if not preorder holds.'
            raise_wrapped(DPInternalError, e, msg, compact=True)

        from mcdp_posets import RcompUnits
        from mcdp_posets import format_pint_unit_short
        from mcdp_posets.maps.identity import IdentityMap


        if isinstance(A, Nat) and isinstance(B, Rcomp):
            from mcdp_posets.maps.coerce_to_int import CoerceToInt
            from mcdp_posets.maps.promote_to_float import PromoteToFloat
            return PromoteToFloat(A, B), CoerceToInt(B, A)

        if isinstance(A, Nat) and isinstance(B, Int):
            return IdentityMap(A, B), IdentityMap(B, A)
            
        if isinstance(A, RcompUnits) and isinstance(B, RcompUnits):
            assert A.units.dimensionality == B.units.dimensionality

            factor = float(B.units / A.units)
            from mcdp_posets.maps.linearmapcomp import LinearMapComp
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

        from mcdp_posets import UpperSets
        if isinstance(A, UpperSets) and isinstance(B, UpperSets):
            P_A_to_B, P_B_to_A = self.get_embedding(A.P, B.P)
            from mcdp_posets.maps.lift_to_uppersets import LiftToUpperSets
            m1 = LiftToUpperSets(P_A_to_B)
            m2 = LiftToUpperSets(P_B_to_A)
            setattr(m1, '__name__', 'L%s' % P_A_to_B.__name__)
            setattr(m1, '__name__', 'L%s' % P_B_to_A.__name__)
            return m1, m2

        from mcdp_posets import FiniteCollectionsInclusion
        if (isinstance(A, FiniteCollectionsInclusion) and
            isinstance(B, FiniteCollectionsInclusion)):
            a_to_b, b_to_a = self.get_embedding(A.S, B.S)
            from mcdp_posets.maps.lift_to_finitecollections import LiftToFiniteCollections
            m1 = LiftToFiniteCollections(a_to_b)
            m2 = LiftToFiniteCollections(b_to_a)
            setattr(m1, '__name__', 'L%s' % a_to_b.__name__)
            setattr(m1, '__name__', 'L%s' % b_to_a.__name__)
            return m1, m2


        msg = 'Spaces are ordered, but you forgot to code embedding.'
        raise_desc(NotImplementedError, msg, A=A, B=B)




def express_value_in_isomorphic_space(S1, s1, S2):
    """ 
        expresses s1 in S2 

        assumes S1 <= S2 
    """
    A_to_B, _ = tu.get_embedding(S1, S2)
    return A_to_B(s1)



def get_product_embedding(tu, A, B):
    pairs = [tu.get_embedding(a, b) for a, b in zip(A, B)]
    fs = [x for x, _ in pairs]
    finv = [y for _, y in pairs]


    from mcdp_posets.maps.product_map import ProductMap
    res = ProductMap(fs), ProductMap(finv)
    return res


def check_leq_products(tu, A, B):
    if len(A) != len(B):
        msg = 'Different length.'
        raise_desc(NotLeq, msg, A=A, B=B)
    for a, b in zip(A, B):
        try:
            tu.check_leq(a, b)
        except NotLeq as e:
            msg = 'Found uncomparable elements.'
            raise_wrapped(NotLeq, e, msg, compact=True, a=a, b=b)


tu = TypesUniverse()

def get_types_universe():
    return tu
