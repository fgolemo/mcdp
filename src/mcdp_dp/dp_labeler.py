from mcdp_dp.primitive import PrimitiveDP
from contracts import contract
import copy
from mocdp import ATTRIBUTE_NDP_RECURSIVE_NAME
from contracts.utils import indent

__all__ = [
    'LabelerDP',
]

class LabelerDP(PrimitiveDP):
    
    @contract(dp=PrimitiveDP, recname='tuple,seq(str)')
    def __init__(self, dp, recname):
        self.dp = dp
        F = dp.get_fun_space()
        R = dp.get_res_space()
        I0 = dp.get_imp_space()
        Imarked = copy.copy(I0)
        setattr(Imarked, ATTRIBUTE_NDP_RECURSIVE_NAME, recname)
        PrimitiveDP.__init__(self, F=F, R=R, I=Imarked)
        self.recname = recname

    def repr_long(self):
        s = 'LabelerDP({})'.format(self.recname)
        s += '\n' + indent(self.dp.repr_long(), ' ')
        return s

    def solve(self, f):
        return self.dp.solve(f)

    def evaluate(self, i):
        return self.dp.evaluate(i)

    def get_implementations_f_r(self, f, r):
        return self.dp.get_implementations_f_r(f, r)
#
#     @contract(returns=Space)
#     def get_imp_space(self):
#         I = self.I
#         # This is a mess... on the up side, the rest of the code is great.
#         #
#         # Note: the first time the dp is created, there is no attribute.
#         #   dp = Series(...)
#         #      <internally calls get_imp_space()>
#         #   setattr(dp, ..., name)
#         # So we need to redo it
#         # if not hasattr(self, 'Imarked'):
#         if not hasattr(self, 'Imarked') or (hasattr(self, ATTRIBUTE_NDP_RECURSIVE_NAME) and not hasattr(self.Imarked, ATTRIBUTE_NDP_RECURSIVE_NAME)):
#             self.Imarked = copy.copy(I)
#             if hasattr(self, ATTRIBUTE_NDP_RECURSIVE_NAME):
#                 x = getattr(self, ATTRIBUTE_NDP_RECURSIVE_NAME)
#
#                 already = getattr(self.Imarked, ATTRIBUTE_NDP_RECURSIVE_NAME, None)
#                 if already is not None and already != x:
#                     msg = 'Overwriting value of ATTRIBUTE_NDP_RECURSIVE_NAME'
#                     raise_desc(DPInternalError, msg, x=x, already=already, xself=self)
#
#                 setattr(self.Imarked, ATTRIBUTE_NDP_RECURSIVE_NAME, x)
#
#         return self.Imarked
