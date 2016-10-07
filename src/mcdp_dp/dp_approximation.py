# -*- coding: utf-8 -*-
import math

from contracts.utils import check_isinstance
from mcdp_posets import Map, MapNotDefinedHere, RcompUnits
from mcdp_posets.rcomp import finfo
from mocdp.comp.wrap import dpwrap
from mocdp.exceptions import mcdp_dev_warning


# 
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
#         try:
#             m = x / self.alpha
#         except FloatingPointError as e:
#             s = str(e)
#             if 'overflow' in s:
#                 m = finfo.max
#             elif 'underflow' in s:
#                 m = finfo.tiny
#             else:
#                 raise
# 
#         n = math.ceil(m)
#         y = n * self.alpha
# 
#         res = float(y)
# 
#         return res
# 
# class LogarithmicCeil():
#     """
#     
#         y = exp( alpha * ceil(log(x) / alpha) )
#         
#     """
# 
#     def __init__(self, alpha):
#         assert alpha > 0, alpha
#         self.alpha = alpha
# 
#     def __call__(self, x):
#         assert isinstance(x, float) and x >= 0, x
#         if math.isinf(x):
#             return float('inf')
#         if x == 0:
#             return 0.0
#         l = math.log10(x)
#         m = l / self.alpha
#         n = math.ceil(m)
#         o = n * self.alpha
#         y = math.pow(10, o)
#         return float(y)
# 
# class CombinedCeil():
#     def __init__(self, n_per_decade, step):
# 
#         alpha = 1.0 / n_per_decade
#         self.f1 = LogarithmicCeil(alpha)
#         self.f2 = LinearCeil(step)
# 
#     def __call__(self, x):
#         xx = self.f1(x)
#         y = self.f2(xx)
#         return y
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


