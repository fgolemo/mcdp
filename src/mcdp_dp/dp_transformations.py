from .primitive import ApproximableDP, PrimitiveDP
from contracts import contract
from contracts.utils import raise_wrapped
from mcdp_dp.dp_loop2 import DPLoop2
from mcdp_dp.dp_parallel_n import ParallelN
from mcdp_posets.space import NotEqual
from mcdp_posets.types_universe import get_types_universe
from mocdp import ATTRIBUTE_NDP_MAKE_FUNCTION, ATTRIBUTE_NDP_RECURSIVE_NAME
from mocdp.exceptions import DPInternalError
from mcdp_dp.opaque_dp import OpaqueDP
from mcdp_dp.dp_labeler import LabelerDP

@contract(dp=PrimitiveDP, returns=PrimitiveDP)
def dp_transform(dp, f):
    """ Recursive application of a map f that is equivariant with
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
    elif isinstance(dp, ParallelN):
        dps = tuple(dp_transform(_, f) for _ in dp.dps)
        return ParallelN(dps)
    elif isinstance(dp, DPLoop0):
        return DPLoop0(dp_transform(dp.dp1, f))
    elif isinstance(dp, DPLoop2):
        return DPLoop2(dp_transform(dp.dp1, f))
    elif isinstance(dp, OpaqueDP):
        return OpaqueDP(dp_transform(dp.dp, f))
    elif isinstance(dp, LabelerDP):
        return LabelerDP(dp_transform(dp.dp, f), dp.recname)
    else:
        r = f(dp)
        # assert isinstance(r, PrimitiveDP)
        return r

# def preserve_dp_attributes(dp1, dp2):
#     """ preserves the attributes of dp1 in dp2 """
#     attrs = [ATTRIBUTE_NDP_RECURSIVE_NAME, ATTRIBUTE_NDP_MAKE_FUNCTION]
#     for a in attrs:
#         if hasattr(dp1, a):
#             setattr(dp2, a, getattr(dp1, a))
#
# def preserve_attributes(f):
#     """ returns a function that applies f but also preserves attributes """
#     def ff(x):
#         y = f(x)
#
#         tu = get_types_universe()
#         I1 = x.get_imp_space()
#         I2 = y.get_imp_space()
#         try:
#             tu.check_equal(I1, I2)
#         except NotEqual as e:
#             msg = 'Invalid transformation of %s -> %s that does not preserve imp space.' % (type(x), type(y))
#             raise_wrapped(DPInternalError, e, msg, I1=1, I2=I2)
#
#         preserve_dp_attributes(x, y)
#         return y
#     return ff

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

