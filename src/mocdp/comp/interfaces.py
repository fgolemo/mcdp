from contracts import contract
from abc import ABCMeta, abstractmethod

__all__ = [
    'NamedDP',
]

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
