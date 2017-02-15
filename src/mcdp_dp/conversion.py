# -*- coding: utf-8 -*-
from contracts import contract
from mcdp_posets import NotLeq, get_types_universe
from mcdp.exceptions import  mcdp_dev_warning

from .dp_generic_unary import WrapAMap
from .primitive import PrimitiveDP


_ = PrimitiveDP

__all__ = [
    'Conversion',
    'get_conversion',
]

class Conversion(WrapAMap):
    """ Simple wrap to WrapAMap to get a custom icon. """


@contract(returns='None|$PrimitiveDP')
def get_conversion(A, B):
    """ Returns None if there is no need for a Conversion Map.
        Otherwise returns a Conversion (< WrapAMap). """
    tu = get_types_universe() 

    if tu.equal(A, B):
        conversion = None
    else:
        try:
            A_to_B, B_to_A = tu.get_super_conversion(A, B)
            mcdp_dev_warning('not really sure of the semantics of this')
            conversion = Conversion(A_to_B, B_to_A)
        except NotLeq:
            raise
        
    return conversion
