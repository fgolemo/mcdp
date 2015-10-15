from abc import abstractmethod, ABCMeta
from contracts.utils import raise_wrapped
from mocdp.exceptions import DPInternalError
from .dp_flatten import Mux
from .dp_identity import Identity
from .dp_parallel import Parallel
from mocdp.posets import PosetProduct
from multi_index.get_it_test import compose_indices

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
        except BaseException as e:
            msg = 'Error while executing Parallel simplification rule.'
            raise_wrapped(DPInternalError, e, msg, dp1=dp1.repr_long(),
                          dp2=dp2.repr_long(), rule=self)
        from mocdp.comp.tests.test_composition import check_same_spaces
        try:
            check_same_spaces(dp0, res)
        except AssertionError as e:
            msg = 'Invalid Parallel simplification for rule.'
            raise_wrapped(DPInternalError, e, msg, dp1=dp1.repr_long(),
                          dp2=dp2.repr_long(), rule=self)
        return res

    @abstractmethod
    def _execute(self, dp1, dp2):
        pass


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
        from .dp_series_simplification import unwrap_as_series_start_last

        _, dp1_last = unwrap_as_series_start_last(dp1)
        return isinstance(dp1_last, Mux)

    def _execute(self, dp1, dp2):
        from .dp_series_simplification import unwrap_as_series_start_last, make_series

        dp1_start, dp1_last = unwrap_as_series_start_last(dp1)
        a = dp1_last.coords
        R = Parallel(dp1_start, dp2).get_res_space()
        coords0 = compose_indices(R, 0, a, list)
        coords = [coords0, 1]
        m = Mux(R, coords)

        x = make_parallel(dp1_start, dp2)

        return make_series(x, m)


class RuleMuxOutsideB(ParSimplificationRule):
#     #  - -- ----------> |
#     #                    | -
#     #  --p2---Mux(a)---> |
#     #  ---- - |
#     #         | ---> Mux(0, [1 * (a)])
#     #  --p2---|

    def applies(self, _, dp2):
        from .dp_series_simplification import unwrap_as_series_start_last

        _, dp2_last = unwrap_as_series_start_last(dp2)
        return isinstance(dp2_last, Mux)

    def _execute(self, dp1, dp2):
        from .dp_series_simplification import unwrap_as_series_start_last, make_series

        dp2_start, dp2_last = unwrap_as_series_start_last(dp2)
        a = dp2_last.coords
        R = Parallel(dp1, dp2_start).get_res_space()
        coords0 = compose_indices(R, 1, a, list)
        coords = [0, coords0]
        m = Mux(R, coords)
        x = make_parallel(dp1, dp2_start)

        return make_series(x, m)

rules = [
    RuleMuxOutside(),
    RuleMuxOutsideB(),
]

def make_parallel(dp1, dp2):
    from mocdp.dp.dp_series_simplification import make_series, is_equiv_to_terminator, equiv_to_identity

#     # if none is a mux, we cannot do anything
#     if not isinstance(dp1, Mux) and not isinstance(dp2, Mux):
#         return Parallel(dp1, dp2)
#
#     def identity_as_mux(x):
#         if isinstance(x, Identity):
#             F = x.get_fun_space()
#             return Mux(F, ())
#         return x
#
#     dp1 = identity_as_mux(dp1)
#     dp2 = identity_as_mux(dp2)


    # change identity to Mux
    a = Parallel(dp1, dp2)
    if equiv_to_identity(dp1) and equiv_to_identity(dp2):
        F = PosetProduct((dp1.get_fun_space(), dp2.get_fun_space()))
        assert F == a.get_fun_space()
        return Identity(F)

    # Parallel(X, Terminator) => Series(Mux([0]), X, Mux([0, ()]))
    if is_equiv_to_terminator(dp2):
        F = a.get_fun_space()  # PosetProduct((dp1.get_fun_space(),))
        m1 = Mux(F, coords=0)
        m2 = dp1
        m3 = Mux(m2.get_res_space(), [(), []])
        res = make_series(make_series(m1, m2), m3)

        assert res.get_res_space() == a.get_res_space()
        assert res.get_fun_space() == a.get_fun_space()
        return res

    if is_equiv_to_terminator(dp1):
        F = a.get_fun_space()  # PosetProduct((dp1.get_fun_space(),))
        m1 = Mux(F, coords=1)
        m2 = dp2
        m3 = Mux(m2.get_res_space(), [[], ()])
        return make_series(make_series(m1, m2), m3)

    for rule in rules:
        if rule.applies(dp1, dp2):
            return rule.execute(dp1, dp2)

    return Parallel(dp1, dp2)
#     # from the right
#     # bring the mux outside the parallel

