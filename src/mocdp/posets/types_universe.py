from contracts.utils import raise_desc, raise_wrapped
from mocdp.posets.poset import NotLeq, Preorder
from mocdp.posets.space import NotEqual, Map

__all__ = ['get_types_universe']



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
            setattr(B_to_A, '__name__', '%s-to-%s-f%.3f' % (b, a, B_to_A.factor))
            setattr(A_to_B, '__name__', '%s-to-%s-f%.3f' % (a, b, A_to_B.factor))
            return A_to_B, B_to_A

        assert False

class LinearMapComp(Map):
    """ Linear multiplication on R + top """

    def __init__(self, A, B, factor):
        Map.__init__(self, A, B)
        self.A = A
        self.B = B
        self.factor = factor
    
    def _call(self, x):
        if self.A.equal(x, self.A.get_top()):
            return self.B.get_Top()
        return x * self.factor


tu = TypesUniverse()

def get_types_universe():
    return tu
