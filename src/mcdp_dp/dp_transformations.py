# -*- coding: utf-8 -*-
from contracts import contract
from mcdp_dp import (
    CoProductDP, CoProductDPLabels, DPLoop2, LabelerDP, OpaqueDP, ParallelN)
from mocdp.exceptions import DPInternalError

from .primitive import ApproximableDP, PrimitiveDP


from contracts.utils import, raise_wrapped


@contract(dp=PrimitiveDP, returns=PrimitiveDP)
def dp_transform(dp, f):
    """ Recursive application of a map f that is equivariant with
        series and parallel operations. """
    from mcdp_dp.dp_series import Series0
    from mcdp_dp.dp_loop import DPLoop0
    from mcdp_dp.dp_parallel import Parallel
    from mcdp_dp.dp_series_simplification import check_same_spaces

    if isinstance(dp, Series0):
        return Series0(dp_transform(dp.dp1, f),
                       dp_transform(dp.dp2, f))
    elif isinstance(dp, Parallel):
        return Parallel(dp_transform(dp.dp1, f),
                       dp_transform(dp.dp2, f))
    elif isinstance(dp, ParallelN):
        dps = tuple(dp_transform(_, f) for _ in dp.dps)
        return ParallelN(dps)
    elif isinstance(dp, CoProductDPLabels):
        return CoProductDPLabels(dp_transform(dp.dp, f), dp.labels)
    elif isinstance(dp, CoProductDP):
        dps2 = tuple(dp_transform(_, f) for _ in dp.dps)
        return CoProductDP(dps2)
    elif isinstance(dp, DPLoop0):
        return DPLoop0(dp_transform(dp.dp1, f))
    elif isinstance(dp, DPLoop2):
        return DPLoop2(dp_transform(dp.dp1, f))
    elif isinstance(dp, OpaqueDP):
        return OpaqueDP(dp_transform(dp.dp, f))
    elif isinstance(dp, LabelerDP):
        return LabelerDP(dp_transform(dp.dp, f), dp.recname)
    else:
        dp2 = f(dp)
        try:
            check_same_spaces(dp, dp2)
        except AssertionError as e:
            msg = 'Transformation %s does not preserve spaces.' % f
            raise_wrapped(DPInternalError, e, msg, dp=dp, dp2=dp2, f=f, compact=True)
        return dp2


@contract(dp=PrimitiveDP, nl='int,>=1', nu='int,>=1')
def get_dp_bounds(dp, nl, nu):
    """ Returns a pair of design problems that are a lower and upper bound. """

    def transform_upper(dp, n):
        if isinstance(dp, ApproximableDP):
            return dp.get_upper_bound(n)
        else:
            return dp

    def transform_lower(dp, n):
        if isinstance(dp, ApproximableDP):
            return dp.get_lower_bound(n)
        else:
            return dp

    preserve_attributes = lambda x : x
    dpU = dp_transform(dp, preserve_attributes(lambda _: transform_upper(_, nu)))
    dpL = dp_transform(dp, preserve_attributes(lambda _: transform_lower(_, nl)))

    return dpL, dpU

