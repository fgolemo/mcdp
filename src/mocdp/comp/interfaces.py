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
