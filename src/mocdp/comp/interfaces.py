from abc import ABCMeta, abstractmethod
from contracts import contract
from contracts.utils import format_dict_long, format_list_long, raise_wrapped
from mocdp.configuration import get_conftools_nameddps
from mocdp.exceptions import DPSemanticError
from mocdp.posets.poset_product import PosetProduct


__all__ = [
    'NamedDP',
    'dp_from_ndp',
]

class NamedDP():
    """ A DP with names """
    __metaclass__ = ABCMeta
    
    @abstractmethod
    def get_dp(self):
        pass

    @abstractmethod
    def check_fully_connected(self):
        # Raise notConnected
        pass

    @abstractmethod
    @contract(returns='list(str)')
    def get_fnames(self):
        pass

    @abstractmethod
    @contract(returns='list(str)')
    def get_rnames(self):
        pass
    
    @abstractmethod
    @contract(rname=str)
    def get_rtype(self, rname):
        pass

    @abstractmethod
    @contract(fname=str)
    def get_ftype(self, fname):
        pass

    def repr_long(self):
        return self.__repr__()

    def get_ftypes(self, signals):
        # Returns the product space
        types = [self.get_ftype(s) for s in signals]
        return PosetProduct(tuple(types))

    def get_rtypes(self, signals):
        # Returns the product space
        types = [self.get_rtype(s) for s in signals]
        return PosetProduct(tuple(types))


class NotConnected(Exception):
    pass
    
class CompositeNamedDP(NamedDP):
    
    """ 
        The only tricky thing is that if there is only one function,
        then F = F1
        but if there are two,
        then F = PosetProduct((F1, F2))
        
        Same thing with the resources.
    
    
    """

    def __init__(self, context):
        self.context = context
        self._rnames = list(self.context.newresources)
        self._fnames = list(self.context.newfunctions)

    def check_fully_connected(self):
        for name, ndp in self.context.names.items():
            try:
                ndp.check_fully_connected()
            except NotConnected as e:
                msg = 'Block %r is not connected.' % name
                raise_wrapped(NotConnected, e, msg)
        from mocdp.lang.blocks import check_missing_connections
        check_missing_connections(self.context)
    
    def get_fnames(self):
        return list(self._fnames)

    def get_rnames(self):
        return list(self._rnames)

    def rindex(self, rn):
        if len(self._rnames) == 1:
            return ()
        return self._rnames.index(rn)

    def findex(self, fn):
        if len(self._fnames) == 1:
            return ()
        return self._fnames.index(fn)
    
    def get_rtype(self, rn):
        ndp = self.context.newresources[rn]
        return ndp.get_rtype(ndp.get_rnames()[0])
        
    def get_ftype(self, fn):
        ndp = self.context.newfunctions[fn]
        return ndp.get_ftype(ndp.get_fnames()[0])

    # @contract(returns=SimpleWrap)
    def abstract(self):
        try:
            self.check_fully_connected()
        except NotConnected as e:
            msg = 'Cannot abstract because not all subproblems are connected.'
            raise_wrapped(DPSemanticError, e, msg)
        
        from mocdp.comp.connection import dpgraph
        context = self.context
        res = dpgraph(context.names, context.connections, split=[])
        return res

    def get_dp(self):
        ndp = self.abstract()
        return ndp.get_dp()

    def __repr__(self):
        s = 'CompositeNDP:'
        for f in self._fnames:
            s += '\n provides %s  [%s]' % (f, self.get_ftype(f))
        for r in self._rnames:
            s += '\n requires %s  [%s]' % (r, self.get_rtype(r))

        s += '\n connections: \n' + format_list_long(self.context.connections, informal=True)
        s += '\n names: \n' + format_dict_long(self.context.names, informal=True)

        return s


def dp_from_ndp(ndp):
    """ Unwrap """
    _, ndp = get_conftools_nameddps().instance_smarter(ndp)
    # unwrap
    return ndp.get_dp()
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
