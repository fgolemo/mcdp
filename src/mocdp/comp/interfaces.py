from contracts import contract
from mocdp.dp.primitive import PrimitiveDP
from contracts.utils import raise_wrapped
from mocdp.posets.poset_product import PosetProduct
from abc import ABCMeta, abstractmethod


class NamedDP():
    """ A DP with names """
    __metaclass__ = ABCMeta
    
    @abstractmethod
    def get_dp(self):
        pass

    @abstractmethod
    @contract(returns='list(str)')
    def get_fnames(self):
        pass

    @abstractmethod
    @contract(returns='list(str)')
    def get_rnames(self):
        pass
    
    def rindex(self, r):
        rnames = self.get_rnames()
        try:
            return rnames.index(r)
        except ValueError:
            msg = 'Cannot find %r in %r.' % (r, rnames)
            raise ValueError(msg)


    def findex(self, f):
        fnames = self.get_fnames()
        try:
            return fnames.index(f)
        except ValueError:
            msg = 'Cannot find %r in %r.' % (f, fnames)
            raise ValueError(msg)

    def get_ftype(self, fname):
        F = self.get_dp().get_fun_space()
        return F[self.findex(fname)]

    def get_ftypes(self, signals):
#         if not signals: raise ValueError('empty')
        # Returns the product space
        types = [self.get_ftype(s) for s in signals]
        return PosetProduct(tuple(types))

    def get_rtype(self, rname):
        R = self.get_dp().get_res_space()
        return R[self.rindex(rname)]

    def get_rtypes(self, signals):
#         if not signals: raise ValueError('empty')
        # Returns the product space
        types = [self.get_rtype(s) for s in signals]
        return PosetProduct(tuple(types))

#
# def parallel(dp1, dp2):
#     pass
#
#
# def interconnect(name2dp, connections):
#     pass

#
# class DPBuilder():
#     def get_required_params(self):
#         pass
#
#     def get_params(self):
#         # di
#         pass
#
#     @contract(returns=DP)
#     def instance(self, config):
#         """ Returns a DP """
#         pass
