# -*- coding: utf-8 -*-
from contracts.utils import check_isinstance
from mcdp_posets import RcompUnits, Rcomp, R_dimensionless

from .dp_misc_unary import CeilDP, Floor0DP
from .dp_multvalue import MultValueDP
from .dp_series_simplification import wrap_series


__all__ = [
    'makeLinearCeilDP',
    'makeLinearFloor0DP',
]

def makeLinearCeilDP(P, alpha):
    """
        Implements the approximation:
        
            y >= ( alpha * ceil(x) / alpha) )
    """
    if alpha <= 0:
        raise ValueError(alpha)
    
    alpha_inv = 1.0 / alpha
    
    check_isinstance(P, (Rcomp, RcompUnits))
    
    if isinstance(P, Rcomp):
        dps = [
            MultValueDP(P, P, P, alpha_inv),
            CeilDP(P, P),
            MultValueDP(P, P, P, alpha),
        ]
        return wrap_series(P, dps)
    elif isinstance(P, RcompUnits):
        dimensionless = R_dimensionless
        dps = [
            MultValueDP(P, P, dimensionless, alpha_inv),
            CeilDP(P, P),
            MultValueDP(P, P, dimensionless, alpha),
        ]
        return wrap_series(P, dps)
    else:
        assert False, P


def makeLinearFloor0DP(P, alpha):
    """
        Implements the approximation:
        
            y >= ( alpha * floor0(x) / alpha) )
            
        where floor0 disagrees with floor on integers.
    """
    if alpha <= 0:
        raise ValueError(alpha)
    
    alpha_inv = 1.0 / alpha
    
    check_isinstance(P, (Rcomp, RcompUnits))
    
    if isinstance(P, Rcomp):
        dps = [
            MultValueDP(P, P, P, alpha_inv),
            Floor0DP(P),
            MultValueDP(P, P, P, alpha),
        ]
        return wrap_series(P, dps)
    elif isinstance(P, RcompUnits):
        dimensionless = R_dimensionless
        dps = [
            MultValueDP(P, P, dimensionless, alpha_inv),
            Floor0DP(P),
            MultValueDP(P, P, dimensionless, alpha),
        ]
        return wrap_series(P, dps)
    else:
        assert False, P

