from contracts.utils import raise_wrapped
from mocdp.dp.dp_identity import Identity
from mocdp.dp.dp_flatten import Mux
from mocdp.posets.poset_product import PosetProduct
from multi_index.get_it_test import compose_indices, get_id_indices
import warnings
from mocdp.dp.dp_series import Series

__all__ = [
    'make_series',
]

def equiv_to_identity(dp):
    if isinstance(dp, Identity):
        return True
    if isinstance(dp, Mux):
        s = simplify_indices_F(dp.get_fun_space(), dp.coords)
        if s == ():
            return True
    return False
#
# def is_permutation(dp):
#     from mocdp.dp.dp_flatten import Mux
#     if not isinstance(dp, Mux):
#         return False
#
#     if dp.coords == [1, 0]:
#         return True
#     # TODO: more options
#     return False
# def is_permutation_invariant(dp):
#     from mocdp.dp import Product, Sum, Min, Max
#     if isinstance(dp, (Max, Min, Sum, Product)):
#         return True
#     # TODO: more options
#     return False

def is_equiv_to_terminator(dp):
    from mocdp.dp.dp_terminator import Terminator
    if isinstance(dp, Terminator):
        return True
#     from mocdp.dp.dp_flatten import Mux
#     if isinstance(dp, Mux) and dp.coords == []:
#         return True
    return False

def make_series(dp1, dp2):
    """ Creates a Series if needed.
        Simplifies the identity and muxes """
    # first, check that the series would be created correctly

    # Series(X(F,R), Terminator(R)) => Terminator(F)
    # but X not loop
#     from mocdp.dp.dp_loop import DPLoop0
    if is_equiv_to_terminator(dp2) and isinstance(dp1, Mux):

        from mocdp.dp.dp_terminator import Terminator
        res = Terminator(dp1.get_fun_space())
#         print('Terminator')
#         print('-dp1: %s' % dp1.repr_long())
#         print('-dp2: %s' % dp2.repr_long())
#         print('-res: %s' % res.repr_long())
        assert res.get_fun_space() == dp1.get_fun_space()
        return res

    if equiv_to_identity(dp1):
        return dp2

    if equiv_to_identity(dp2):
        return dp1
#
#     if is_permutation(dp1) and is_permutation_invariant(dp2):
#         # wrong, because the types might not match
#         # need to permute the types of dp2
#         return dp2


#     a = Series0(dp1, dp2)

    from mocdp.dp.dp_parallel import Parallel
    from mocdp.dp.dp_parallel_simplification import make_parallel

    if isinstance(dp1, Parallel) and isinstance(dp2, Parallel):
        a = make_series(dp1.dp1, dp2.dp1)
        b = make_series(dp1.dp2, dp2.dp2)
        return make_parallel(a, b)


    if isinstance(dp1, Mux) and isinstance(dp2, Mux):
        return mux_composition(dp1, dp2)

    if isinstance(dp1, Mux):
        if isinstance(dp2, Series):
            dps = unwrap_series(dp2)
            if isinstance(dps[0], Mux):
                first = mux_composition(dp1, dps[0])
                rest = reduce(make_series, dps[1:])
                return make_series(first, rest)

        from mocdp.dp.dp_parallel import Parallel
        def has_null_fun(dp):
            F = dp.get_fun_space()
            return isinstance(F, PosetProduct) and len(F) == 0

        if isinstance(dp2, Parallel):
            if isinstance(dp2.dp1, Identity) and has_null_fun(dp2.dp1):
                assert len(dp1.coords) == 2  # because it is followed by parallel
                assert dp1.coords[0] == []  # because it's null
                x = dp1.coords[1]
                A = Mux(dp1.get_fun_space(), x)
                B = dp2.dp2
                C = Mux(B.get_res_space(), [[], ()])
                return make_series(make_series(A, B), C)

            if isinstance(dp2.dp2, Identity) and has_null_fun(dp2.dp2):
                assert len(dp1.coords) == 2  # because it is followed by parallel
                assert dp1.coords[1] == []  # because it's null
                x = dp1.coords[0]
                A = Mux(dp1.get_fun_space(), x)
                B = dp2.dp1
                C = Mux(B.get_res_space(), [(), []])
                return make_series(make_series(A, B), C)

        if isinstance(dp2, Series):
            dps = unwrap_series(dp2)

            def has_null_identity(dp):
                assert isinstance(dp, Parallel)
                if isinstance(dp.dp1, Identity) and has_null_fun(dp.dp1):
                    return True
                if isinstance(dp.dp2, Identity) and has_null_fun(dp.dp2):
                    return True
                return False

            if isinstance(dps[0], Parallel) and has_null_identity(dps[0]):
                first = make_series(dp1, dps[0])
                rest = reduce(make_series, dps[1:])
                return make_series(first, rest)


    from mocdp.dp.dp_parallel_simplification import make_parallel
    from mocdp.comp.tests.test_composition import check_same_spaces

    # bring the mux outside the parallel
    #                   | - Mux(c) - p1
    #  Mux([a,b]) ----> |
    #                   | -
    #                     | - p1
    #  Mux([a*c,b]) ----> |
    #                     |
    if isinstance(dp1, Mux) and isinstance(dp2, Parallel) \
        and isinstance(unwrap_series(dp2.dp1)[0], Mux):

        unwrapped = unwrap_series(dp2.dp1)
        first_mux = unwrapped[0]
        assert isinstance(first_mux, Mux)

        coords = dp1.coords
        assert isinstance(coords, list) and len(coords) == 2, coords

        F = dp1.get_fun_space()
        coords2 = [compose_indices(F, coords[0], first_mux.coords, list), coords[1]]
        m2 = Mux(F, coords2)

        rest = wrap_series(first_mux.get_res_space(), unwrapped[1:])

        res = make_series(m2, make_parallel(rest, dp2.dp2))

        check_same_spaces(Series(dp1, dp2), res)
        return res

    if isinstance(dp1, Mux) and isinstance(dp2, Parallel) \
        and isinstance(unwrap_series(dp2.dp2)[0], Mux):

        unwrapped = unwrap_series(dp2.dp2)
        first_mux = unwrapped[0]
        assert isinstance(first_mux, Mux)

        coords = dp1.coords
        assert isinstance(coords, list) and len(coords) == 2, coords

        F = dp1.get_fun_space()
        coords2 = [coords[0], compose_indices(F, coords[1], first_mux.coords, list)]
        m2 = Mux(F, coords2)

        rest = wrap_series(first_mux.get_res_space(), unwrapped[1:])

        res = make_series(m2, make_parallel(dp2.dp1, rest))

        check_same_spaces(Series(dp1, dp2), res)
        return res

#     # from the right
#     # bring the mux outside the parallel
#     #  - p1 - Mux(a) --> |
#     #                    | -
#     #  ----------------> |
#     #  - p1 - |-Mux(a)-|
#     #         |        | -
#     #  -------|--------|

#     #  - p1 - |
#     #         | ---> Mux( [0 * (a)], 1 )
#     #  -------|
#     if isinstance(dp2, Mux) and isinstance(dp1, Parallel) \
#         and isinstance(unwrap_series(dp1.dp1)[-1], Mux):
#
#         unwrapped = unwrap_series(dp1.dp1)
#         last_mux = unwrapped[-1]
#         assert isinstance(last_mux, Mux)
#
#         coords = dp2.coords
#         assert isinstance(coords, list) and len(coords) == 2, coords
#
#         F = dp1.get_fun_space()
#         coords2 = [compose_indices(F, coords[0], first_mux.coords, list), coords[1]]
#         m2 = Mux(F, coords2)
#
#         rest = wrap_series(first_mux.get_res_space(), unwrapped[1:])
#
#         res = make_series(m2, make_parallel(rest, dp2.dp2))
#
#         check_same_spaces(Series0(dp1, dp2), res)
#         return res


    if isinstance(dp2, Mux):
        if isinstance(dp1, Series):
            dps = unwrap_series(dp1)
            if isinstance(dps[-1], Mux):
                last = mux_composition(dps[-1], dp2)
                rest = reduce(make_series, dps[:-1])
                return make_series(rest, last)

#     print('Cannot simplify:')
#     print(' dp1: %s' % dp1)
#     print(' dp2: %s' % dp2)
#     print('\n- '.join([str(x) for x in unwrap_series(a)]))
    return Series(dp1, dp2)

def unwrap_series(dp):
    if not isinstance(dp, Series):
        return [dp]
    else:
        return unwrap_series(dp.dp1) + unwrap_series(dp.dp2)

def unwrap_as_series_start_last(dp):
    dpu = unwrap_series(dp)
    dpu_last = dpu[-1]
    dpu_start = wrap_series(dp.get_fun_space(), dpu[:-1])
    return dpu_start, dpu_last


def wrap_series(F0, dps):
    if len(dps) == 0:
        return Identity(F0)
    else:
        return make_series(dps[0], wrap_series(dps[0].get_res_space(), dps[1:]))

def simplify_indices_F(F, coords):
    # Safety check: Clearly if it's not the identity it cannot be equal to ()
    from mocdp.dp.dp_flatten import get_R_from_F_coords
    R = get_R_from_F_coords(F, coords)
    if not (R == F):
        return coords

    # generic test
    i0 = get_id_indices(F)
    # compose
    i0coords = compose_indices(F, i0, coords, list)
    if i0 == i0coords:
        return ()

    if coords == [0] and len(F) == 1:
        return ()
    if coords == [0, 1] and len(F) == 2:
        return ()
    if coords == [0, (1,)] and len(F) == 2:
        return ()
    if coords == [0, 1, 2] and len(F) == 3:
        return ()

    warnings.warn('need a double check here')
    if coords == [[(0, 0)], [(1, 0)]]:
        return ()

    if coords == [[(0, 0)], [(1, 0), (1, 1)]]:
        return ()

    # [[(0, 1)], [(1, 0), (0, 0)]]
    return coords

def mux_composition(dp1, dp2):
    try:
        dp0 = Series(dp1, dp2)
        assert isinstance(dp1, Mux)
        assert isinstance(dp2, Mux)
        F = dp1.get_fun_space()
        c1 = dp1.coords
        c2 = dp2.coords
        coords = compose_indices(F, c1, c2, list)
#         print('coords: %s' % str(coords))
        coords = simplify_indices_F(F, coords)

        #     if x == [0]:
#         return ()
#     if x == [0, 1]:
#         return ()
#     # TODO: do it general
#     if x == [0, (1,)]:
#         return ()
#     if x == [0, 1, 2]:
#         return ()


#         print('simpli: %s' % str(coords))
        res = Mux(F, coords)

#         print('dp1: %s' % dp1)
#         print('dp2: %s' % dp2)
#         print('res: %s' % res)
        assert res.get_res_space() == dp0.get_res_space()

        return res
    except Exception as e:
        msg = 'Cannot create shortcut.'
        raise_wrapped(Exception , e , msg, dp1=dp1, dp2=dp2,)

