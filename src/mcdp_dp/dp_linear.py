# # -*- coding: utf-8 -*-
# from contracts import contract
# from mcdp_dp import PrimitiveDP
# from mcdp_posets import PosetProduct, Rcomp
# from mcdp.exceptions import mcdp_dev_warning
#
#
# __all__ = [
#     'Linear',
# ]
#
# mcdp_dev_warning('To change')
#
# class Linear(PrimitiveDP):
#
#     @contract(a='float|int', F='$Rcomp|str|None', R='$Rcomp|str|None')
#     def __init__(self, a, F=None, R=None):
#         if F is None:
#             F = Rcomp()
#         if R is None:
#             R = Rcomp()
#         self.a = float(a)
#
#         M = PosetProduct(())
#         PrimitiveDP.__init__(self, F=F, R=R, M=M)
#
#     def solve(self, func):
#         r = self.F.multiply(func, self.a)
#
#         return self.R.U(r)
#
#     def __repr__(self):
#         return 'Linear(%r)' % self.F.format(self.a)


