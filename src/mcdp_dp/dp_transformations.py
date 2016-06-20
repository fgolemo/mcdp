from contracts import contract
from .primitive import PrimitiveDP, ApproximableDP

@contract(dp=PrimitiveDP, returns=PrimitiveDP)
def dp_transform(dp, f):
    """ Recursive application of a map f that commutes with
        series and parallel operations. """
    from mcdp_dp.dp_series import Series0
    from mcdp_dp.dp_loop import DPLoop0
    from mcdp_dp.dp_parallel import Parallel

    if isinstance(dp, Series0):
        return Series0(dp_transform(dp.dp1, f),
                       dp_transform(dp.dp2, f))
    elif isinstance(dp, Parallel):
        return Parallel(dp_transform(dp.dp1, f),
                       dp_transform(dp.dp2, f))
        # todo: parallel n
    elif isinstance(dp, DPLoop0):
        return DPLoop0(dp_transform(dp.dp1, f))
    else:
        r = f(dp)
        # assert isinstance(r, PrimitiveDP)
        return r


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

    dpU = dp_transform(dp, lambda _: transform_upper(_, nu))
    dpL = dp_transform(dp, lambda _: transform_lower(_, nl))

    return dpL, dpU

