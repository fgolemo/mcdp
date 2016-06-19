from contracts import contract
from contracts.utils import raise_wrapped
from mcdp_dp import WrapAMap, PrimitiveDP  # @UnusedImport
from mcdp_posets import NotLeq, get_types_universe
from mocdp.exceptions import DPSemanticError

__all__ = [
    'Conversion',
    'get_conversion',
]

class Conversion(WrapAMap):
    """ Simple wrap to get icon """
    pass

@contract(returns='None|$PrimitiveDP')
def get_conversion(A, B):
    """ Returns None if there is no need or a Conversion Map """
    tu = get_types_universe()
    try:
        tu.check_leq(A, B)
    except NotLeq as e:
        msg = 'Wrapping with incompatible units.'
        raise_wrapped(DPSemanticError, e, msg, A=A, B=B)

    if tu.equal(A, B):
        conversion = None
    else:
        A_to_B, _ = tu.get_embedding(A, B)
        conversion = Conversion(A_to_B)

    return conversion
