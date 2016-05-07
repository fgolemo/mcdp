from contracts import contract
from mocdp.comp.interfaces import NamedDP
from mocdp.posets.space import Space, Map, MapNotDefinedHere
from contracts.utils import raise_desc

import math
from mocdp.comp.context import Connection

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

        m = x / self.alpha
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

    def __init__(self, S, alpha, step, max_value):
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
        return ('CombinedCeil(alpha=%s, step=%s, max_value=%s)' %
                (self.alpha, self.step, self.max_value))

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

def make_approximation_r(name, approx_perc, approx_abs, approx_abs_S,
                         max_value, max_value_S, ndp):
    from mocdp.comp.connection import connect2
    R = ndp.get_rtype(name)
    ndp_after = get_approx_dp(R, name, approx_perc, approx_abs, approx_abs_S, max_value, max_value_S)
    connections = set([Connection('*', name, '*', name)])
    ndp2 = connect2(ndp, ndp_after, connections, split=[], repeated_ok=True)
    return ndp2

def make_approximation_f(name, approx_perc, approx_abs, approx_abs_S,
                         max_value, max_value_S, ndp):
    from mocdp.comp.connection import connect2
    F = ndp.get_ftype(name)
    ndp_before = get_approx_dp(F, name, approx_perc, approx_abs, approx_abs_S, max_value, max_value_S)
    connections = set([Connection('*', name, '*', name)])
    ndp2 = connect2(ndp_before, ndp, connections, split=[], repeated_ok=True)
    return ndp2


def get_approx_dp(S, name, approx_perc, approx_abs, approx_abs_S, max_value, max_value_S):

    from mocdp.dp.dp_generic_unary import WrapAMap
    from mocdp.comp.wrap import dpwrap
    from mocdp.posets.types_universe import express_value_in_isomorphic_space

    approx_abs_ = express_value_in_isomorphic_space(S1=approx_abs_S, s1=approx_abs, S2=S)
    max_value_ = express_value_in_isomorphic_space(S1=max_value_S, s1=max_value, S2=S)

    alpha = approx_perc / 100.0
    print('alpha: %s approx_abs: %s' % (alpha, approx_abs_S.format(approx_abs_)))
    ccm = CombinedCeilMap(S, alpha=alpha, step=approx_abs_, max_value=max_value_)
    dp = WrapAMap(ccm)
    ndp = dpwrap(dp, name, name)
    return ndp


