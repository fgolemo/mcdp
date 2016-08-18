from contracts import contract
from contracts.utils import check_isinstance, raise_desc
from mcdp_dp.dp_identity import Identity
from mcdp_posets import Map, MapNotDefinedHere, RcompUnits, Space
from mocdp.comp.composite import CompositeNamedDP
from mocdp.comp.context import (Connection, get_name_for_fun_node,
    get_name_for_res_node)
from mocdp.comp.interfaces import NamedDP
from mocdp.comp.wrap import dpwrap
from mocdp.exceptions import mcdp_dev_warning
import math
from mcdp_posets.rcomp import finfo


class LinearCeil():
    """
    
        y = ( alpha * ceil(x) / alpha) )
        
    """

    def __init__(self, alpha):
        self.alpha = alpha

    def __call__(self, x):
        assert isinstance(x, float) and x >= 0, x
        if math.isinf(x):
            return float('inf')
        if x == 0.0:
            return 0.0

        try:
            m = x / self.alpha
        except FloatingPointError as e:
            assert 'overflow' in str(e)
            m = finfo.max

        n = math.ceil(m)
        y = n * self.alpha

        res = float(y)

        return res


class LogarithmicCeil():
    """
    
        y = exp( alpha * ceil(log(x) / alpha) )
        
    """

    def __init__(self, alpha):
        assert alpha > 0, alpha
        self.alpha = alpha

    def __call__(self, x):
        assert isinstance(x, float) and x >= 0, x
        if math.isinf(x):
            return float('inf')
        if x == 0:
            return 0.0
        l = math.log10(x)
        m = l / self.alpha
        n = math.ceil(m)
        o = n * self.alpha
        y = math.pow(10, o)
        return float(y)

class CombinedCeil():
    def __init__(self, n_per_decade, step):

        alpha = 1.0 / n_per_decade
        self.f1 = LogarithmicCeil(alpha)
        self.f2 = LinearCeil(step)

    def __call__(self, x):
        xx = self.f1(x)
        y = self.f2(xx)
        return y


def identity(x):
    return x

class CombinedCeilMap(Map):

    def __init__(self, S, alpha, step, max_value=None):
        Map.__init__(self, dom=S, cod=S)
        self.max_value = max_value

        if alpha > 0:
            self.f1 = LogarithmicCeil(alpha)
        else:
            self.f1 = identity
        
        if step > 0:
            self.f2 = LinearCeil(step)
        else:
            self.f2 = identity

        self.alpha = alpha
        self.step = step

    def __repr__(self):
        if self.alpha > 0:  # or self.max_value > 0:
            mcdp_dev_warning('todo: self.max_value')
            return ('CombinedCeil(alpha=%s, step=%s, max_value=%s)' %
                    (self.alpha, self.step, self.max_value))
        else:
            return 'Discretize(%s)' % self.dom.format(self.step)

    def _call(self, x):
        top = self.dom.get_top()

        if self.max_value is not None:
            if not self.dom.leq(x, self.max_value):
                raise MapNotDefinedHere()

        if self.dom.equal(top, x):
            return top
        xx = self.f1(x)
        y = self.f2(xx)
        return y

#
# class LinearCeil():
#     """
#
#         y = ( alpha * ceil(x) / alpha) )
#
#     """
#
#     def __init__(self, alpha):
#         self.alpha = alpha
#
#     def __call__(self, x):
#         assert isinstance(x, float) and x >= 0, x
#         if math.isinf(x):
#             return float('inf')
#         if x == 0.0:
#             return 0.0
#
#         m = x / self.alpha
#         n = math.ceil(m)
#         y = n * self.alpha
#
#         res = float(y)
#
#         return res

class FloorStepMap(Map):

    def __init__(self, S, step):
        check_isinstance(S, RcompUnits)
        Map.__init__(self, dom=S, cod=S)
        self.step = step

    def __repr__(self):
        return 'FloorStep(%s)' % self.dom.format(self.step)

    def _call(self, x):
        top = self.dom.get_top()
        if self.dom.equal(top, x):
            return top

        assert isinstance(x, float)

        try:
            m = x / self.step
        except FloatingPointError as e:
            assert 'overflow' in str(e)
            m = finfo.max

        n = math.floor(m)
        y = n * self.step
        return y

@contract(name=str,
          approx_perc='float|int',
          approx_abs='float|int', approx_abs_S=Space, ndp=NamedDP,
          returns=NamedDP)
def make_approximation(name, approx_perc, approx_abs, approx_abs_S, max_value, max_value_S, ndp):
    fnames = ndp.get_fnames()
    rnames = ndp.get_rnames()

    if name in fnames:
        return make_approximation_f(name, approx_perc, approx_abs, approx_abs_S,
                                    max_value, max_value_S, ndp)

    if name in rnames:
        return make_approximation_r(name, approx_perc, approx_abs, approx_abs_S,
                                    max_value, max_value_S, ndp)

    msg = 'Could not find name in either functions or resources.'
    raise_desc(ValueError, msg, fnames=fnames, rnames=rnames, name=name)


NAME_ORIGINAL = '_original'
NAME_APPROX = '_approx'

def make_approximation_r(name, approx_perc, approx_abs, approx_abs_S,
                         max_value, max_value_S, ndp):
    R = ndp.get_rtype(name)
    ndp_after = get_approx_dp(R, name, approx_perc, approx_abs, approx_abs_S, max_value, max_value_S)

    name2ndp = {NAME_ORIGINAL: ndp, NAME_APPROX: ndp_after}
    fnames = ndp.get_fnames()
    rnames = ndp.get_rnames()

    connections = []
    connections.append(Connection(NAME_ORIGINAL, name, NAME_APPROX, name))

    for fn in fnames:
        F = ndp.get_ftype(fn)
        fn_ndp = dpwrap(Identity(F), fn, fn)
        fn_name = get_name_for_fun_node(fn)
        name2ndp[fn_name] = fn_ndp
        connections.append(Connection(fn_name, fn, NAME_ORIGINAL, fn))

    for rn in rnames:
        R = ndp.get_rtype(rn)
        rn_ndp = dpwrap(Identity(R), rn, rn)
        rn_name = get_name_for_res_node(rn)
        name2ndp[rn_name] = rn_ndp
        if rn == name:
            connections.append(Connection(NAME_APPROX, rn, rn_name, rn))
        else:
            connections.append(Connection(NAME_ORIGINAL, rn, rn_name, rn))

    return CompositeNamedDP.from_parts(name2ndp, connections, fnames, rnames)

def make_approximation_f(name, approx_perc, approx_abs, approx_abs_S,
                         max_value, max_value_S, ndp):
    F = ndp.get_ftype(name)
    ndp_before = get_approx_dp(F, name, approx_perc, approx_abs, approx_abs_S, max_value, max_value_S)

    name2ndp = {NAME_ORIGINAL: ndp, NAME_APPROX: ndp_before}
    fnames = ndp.get_fnames()
    rnames = ndp.get_rnames()

    connections = []
    connections.append(Connection(NAME_APPROX, name, NAME_ORIGINAL, name))

    for fn in fnames:
        F = ndp.get_ftype(fn)
        fn_ndp = dpwrap(Identity(F), fn, fn)
        fn_name = get_name_for_fun_node(fn)
        name2ndp[fn_name] = fn_ndp
        if fn == name:
            connections.append(Connection(fn_name, fn, NAME_APPROX, fn))
        else:
            connections.append(Connection(fn_name, fn, NAME_ORIGINAL, fn))

    for rn in rnames:
        R = ndp.get_rtype(rn)
        rn_ndp = dpwrap(Identity(R), rn, rn)
        rn_name = get_name_for_res_node(rn)
        name2ndp[rn_name] = rn_ndp
        connections.append(Connection(NAME_ORIGINAL, rn, rn_name, rn))

    return CompositeNamedDP.from_parts(name2ndp, connections, fnames, rnames)


def get_approx_dp(S, name, approx_perc, approx_abs, approx_abs_S, max_value, max_value_S):

    from mcdp_dp.dp_generic_unary import WrapAMap
    from mcdp_posets.types_universe import express_value_in_isomorphic_space

    approx_abs_ = express_value_in_isomorphic_space(S1=approx_abs_S, s1=approx_abs, S2=S)
    max_value_ = express_value_in_isomorphic_space(S1=max_value_S, s1=max_value, S2=S)

    alpha = approx_perc / 100.0
    # print('alpha: %s approx_abs: %s' % (alpha, approx_abs_S.format(approx_abs_)))
    ccm = CombinedCeilMap(S, alpha=alpha, step=approx_abs_, max_value=max_value_)
    dp = WrapAMap(ccm)
    ndp = dpwrap(dp, name, name)
    return ndp


