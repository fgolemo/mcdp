# -*- coding: utf-8 -*-
from abc import ABCMeta, abstractmethod

from contracts import contract
from contracts.utils import raise_wrapped
from mcdp_posets import PosetProduct
from mocdp.exceptions import DPInternalError, mcdp_dev_warning
from multi_index.get_it_test import compose_indices

from .dp_flatten import Mux
from .dp_identity import Identity
from .dp_parallel import Parallel
from .dp_parallel_n import ParallelN
from .primitive import PrimitiveDP  # @UnusedImport
from mcdp_posets.uppersets import upperset_product, lowerset_product
from mcdp_dp.dp_constant import Constant, ConstantMinimals
from mcdp_dp.dp_limit import Limit, LimitMaximals
from mcdp_dp.dp_series import Series
from mcdp_dp.primitive import NotSolvableNeedsApprox


__all__ = [
    'make_parallel',
]

class ParSimplificationRule():
    __metaclass__ = ABCMeta

    @abstractmethod
    def applies(self, dp1, dp2):
        """ Returns true if it applies. """

    def execute(self, dp1, dp2):
        """ Returns the simplified version. """
        # check that everything is correct
        dp0 = Parallel(dp1, dp2)
        try:
            res = self._execute(dp1, dp2)
        except BaseException as e: # pragma: no cover
            msg = 'Error while executing Parallel simplification rule %s.' % type(self).__name__
            raise_wrapped(DPInternalError, e, msg, dp1=dp1.repr_long(),
                          dp2=dp2.repr_long(), rule=self)

        try:
            from mcdp_dp.dp_series_simplification import check_same_spaces
            check_same_spaces(dp0, res)
        except AssertionError as e: # pragma: no cover
            msg = 'Invalid Parallel simplification rule %s.' % type(self).__name__
            raise_wrapped(DPInternalError, e, msg, dp1=dp1.repr_long(),
                          dp2=dp2.repr_long(), res=res.repr_long(), rule=self)
        return res

    @abstractmethod
    def _execute(self, dp1, dp2):
        """ Execute the rule """


class RuleMuxOutside(ParSimplificationRule):
#     #  - p1 - Mux(a) --> |
#     #                    | -
#     #  ----------------> |
#     #  - p1 - |-Mux(a)-|
#     #         |        | -
#     #  -------|--------|
#     #  - p1 - |
#     #         | ---> Mux( [0 * (a)], 1 )
#     #  -------|

    def applies(self, dp1, _):

        from mcdp_dp.dp_series_simplification import unwrap_as_series_start_last
        _, dp1_last = unwrap_as_series_start_last(dp1)
        return isinstance(dp1_last, Mux)

    def _execute(self, dp1, dp2):

        from mcdp_dp.dp_series_simplification import unwrap_as_series_start_last
        dp1_start, dp1_last = unwrap_as_series_start_last(dp1)
        a = dp1_last.coords
        R = Parallel(dp1_start, dp2).get_res_space()
        coords0 = compose_indices(R, 0, a, list)
        coords = [coords0, 1]
        m = Mux(R, coords)

        x = make_parallel(dp1_start, dp2)

        from .dp_series_simplification import make_series
        return make_series(x, m)


class RuleMuxOutsideB(ParSimplificationRule):
#     #  - -- ----------> |
#     #                    | -
#     #  --p2---Mux(a)---> |
#     #  ---- - |
#     #         | ---> Mux(0, [1 * (a)])
#     #  --p2---|

    def applies(self, _, dp2):
        from mcdp_dp.dp_series_simplification import unwrap_as_series_start_last
        _, dp2_last = unwrap_as_series_start_last(dp2)
        return isinstance(dp2_last, Mux)

    def _execute(self, dp1, dp2):
        from mcdp_dp.dp_series_simplification import unwrap_as_series_start_last
        dp2_start, dp2_last = unwrap_as_series_start_last(dp2)
        a = dp2_last.coords
        R = Parallel(dp1, dp2_start).get_res_space()
        coords0 = compose_indices(R, 1, a, list)
        coords = [0, coords0]
        m = Mux(R, coords)
        x = make_parallel(dp1, dp2_start)

        from .dp_series_simplification import make_series
        return make_series(x, m)

class RuleEvaluateParIfConstant(ParSimplificationRule):
    """ 
    
        This is really simplification for Par, not for series
        
        Suppose
        
            dp1 = Parallel(a, b)
            
        and a.F = b.F = 1.
        
        so that dp1 = 1 x 1
        
        Then we can evaluate and replace with a constant:
        
            Parallel(a, b) = Series( 1 x 1 -> 1, 
                            ConstantMinimals(a.solve_f(()) x b.solve_f(())))   
           
    """
    def applies(self, dp1, dp2):
        a = dp1
        b = dp2
        
        One = PosetProduct(())
        if not (a.get_fun_space() == One and b.get_fun_space() == One):
            return False
        
        try:
            solutions_a = a.solve(())
            solutions_b = b.solve(())
        except NotSolvableNeedsApprox:
            return False
        
        return True
    
    def _execute(self, dp1, dp2):
        One = PosetProduct(())
        OneOne = PosetProduct((One, One))
        mux = Mux(OneOne, [])

        One = PosetProduct(())
        a = dp1
        b = dp2
        assert a.get_fun_space() == One and b.get_fun_space() == One
        try:
            solutions_a = a.solve(())
            solutions_b = b.solve(())
        except NotSolvableNeedsApprox:
            raise
        
        prod = upperset_product(solutions_a, solutions_b)
        R = PosetProduct((a.get_res_space(), b.get_res_space()))
        if len(prod.minimals) == 1:
            dpconstant = Constant(R, list(prod.minimals)[0])
        else:
            dpconstant = ConstantMinimals(R, prod.minimals)

        res = Series(mux, dpconstant)
        return res

class RuleEvaluateParIfLimit(ParSimplificationRule):
    """ 
    
        This is really simplification for Par, not for series
        
        Suppose
        
            dp1 = Parallel(a, b)
            
        and a.R = b.R = 1.
        
        so that dp1.R = 1 x 1
        
        Then we can evaluate and replace with a constant:
        
            Parallel(a, b) = Series(Limit(a.solve_r(()) x b.solve_r(()))), 1 <-> 1 x 1) 
           
    """
    def applies(self, dp1, dp2):        
        a = dp1
        b = dp2
        
        One = PosetProduct(())
        if not (a.get_res_space() == One and b.get_res_space() == One):
            return False

        try:
            solutions_a = a.solve_r(())  # @UnusedVariable
            solutions_b = b.solve_r(())  # @UnusedVariable
        except NotSolvableNeedsApprox:
            return False
        
        return True

    def _execute(self, dp1, dp2): 
        a = dp1
        b = dp2
        One = PosetProduct(())
        assert a.get_res_space() == One and b.get_res_space() == One
        
        mux = Mux(One, [(), ()])
         
        solutions_a = a.solve_r(())
        solutions_b = b.solve_r(())
        prod = lowerset_product(solutions_a, solutions_b)
        F = PosetProduct((a.get_fun_space(), b.get_fun_space()))
        elements = prod.maximals
        if len(elements) == 1:
            e = list(elements)[0]
            F.belongs(e)
            dpconstant = Limit(F, e)
        else:
            dpconstant = LimitMaximals(F, elements)

        res = Series( dpconstant, mux)
        return res

    
rules = [
    RuleMuxOutside(),
    RuleMuxOutsideB(),
    RuleEvaluateParIfLimit(),
    RuleEvaluateParIfConstant(),
]


# @contract(dps='list[>=2]($PrimitiveDP)')
@contract(dps='list[>=0]($PrimitiveDP)')
def make_parallel_n(dps):
    if len(dps) == 2:
        return make_parallel(dps[0], dps[1])

    if len(dps) == 0:
        mcdp_dev_warning('This works but should be a special case.')

    return ParallelN(tuple(dps))
#
#     from mcdp_dp.dp_series_simplification import make_series
#
#     if len(dps) == 2:
#         return make_parallel(dps[0], dps[1])
#     else:
#         l = make_parallel(dps[-2], dps[-1])
#         dp0 = make_parallel_n(dps[:-2] + [l])
#         mm = get_flatten_muxmap(dp0.get_fun_space())
#         print dp0
#         R0 = dp0.get_res_space()
#         flatten = Mux(R0, mm)
#         print flatten
#         dp = make_series(dp0, flatten)
#         # XXX: what about the prefix?
#         return dp
    
def make_parallel(dp1, dp2):
    from mcdp_dp.dp_series_simplification import disable_optimization
    if disable_optimization:
        return Parallel(dp1, dp2)

    from mcdp_dp.dp_series_simplification import make_series, equiv_to_identity

    # change identity to Mux
    a = Parallel(dp1, dp2)
    if equiv_to_identity(dp1) and equiv_to_identity(dp2):
        F = PosetProduct((dp1.get_fun_space(), dp2.get_fun_space()))
        assert F == a.get_fun_space()
        return Identity(F)

#     if False:
#         # These never run...
#             
#         # Parallel(X, Terminator) => Series(Mux([0]), X, Mux([0, ()]))
#         if is_equiv_to_terminator(dp2):
#             F = a.get_fun_space()  # PosetProduct((dp1.get_fun_space(),))
#             m1 = Mux(F, coords=0)
#             m2 = dp1
#             m3 = Mux(m2.get_res_space(), [(), []])
#             res = make_series(make_series(m1, m2), m3)
#     
#             assert res.get_res_space() == a.get_res_space()
#             assert res.get_fun_space() == a.get_fun_space()
#             return res
#     
#         if is_equiv_to_terminator(dp1):
#             F = a.get_fun_space()  # PosetProduct((dp1.get_fun_space(),))
#             m1 = Mux(F, coords=1)
#             m2 = dp2
#             m3 = Mux(m2.get_res_space(), [[], ()])
#             return make_series(make_series(m1, m2), m3)

    for rule in rules:
        if rule.applies(dp1, dp2):
            logger.debug('Applying par. simplification rule %s' % type(rule).__name__)
            return rule.execute(dp1, dp2)

    return Parallel(dp1, dp2)

from mocdp import logger
