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
        
        context = self.context
        res = dpgraph_making_sure_no_reps(context.names,
                                          context.newfunctions, 
                                          context.newresources,
                                          context.connections)
        return res

    def get_dp(self):
        ndp = self.abstract()
        return ndp.get_dp()

    def __repr__(self):
        s = 'CompositeNDP'
        for f in self._fnames:
            s += '\n provides %s  [%s]' % (f, self.get_ftype(f))
        for r in self._rnames:
            s += '\n requires %s  [%s]' % (r, self.get_rtype(r))

        s += '\n connections: \n' + format_list_long(self.context.connections, informal=True)
        s += '\n names: \n' + format_dict_long(self.context.names, informal=True)
        return s

def dpgraph_making_sure_no_reps(name2dp, newfunctions, newresources, connections):
    from mocdp.comp.connection import dpgraph
    from collections import defaultdict
    # functionname -> list of names that use it
    functions = defaultdict(lambda: list())
    resources = defaultdict(lambda: list())
    for name, ndp in newfunctions.items():
        functions[ndp.get_fnames()[0]].append(name)
    for name, ndp in newresources.items():
        resources[ndp.get_rnames()[0]].append(name)
    
    
    for name, ndp in name2dp.items():
        if name in newfunctions: continue
        for fn in ndp.get_fnames():

            if len(functions[fn]) != 0:
                print('need to translate F (%s, %s) because already in %s' %
                      (name, fn, functions[fn]))

                fn2 = '_%s_%s' % (name, fn)

                return dpgraph_translate_fn(name2dp, newfunctions, newresources,
                                            connections, name, fn, fn2)

            functions[fn].append(name)
                
    for name, ndp in name2dp.items():
        if name in newresources: continue
        for rn in ndp.get_rnames():

            if len(resources[rn]) != 0:
                print('need to translate R (%s, %s) because already in %s' %
                       (name, rn, resources[rn]))

                rn2 = '_%s_%s' % (name, rn)

                return dpgraph_translate_rn(name2dp, newfunctions, newresources,
                                            connections, name, rn, rn2)

            resources[rn].append(name)
    
    res = dpgraph(name2dp, connections, split=[])
    return res

def dpgraph_translate_rn(name2dp, newfunctions, newresources, connections, 
                         name, rn, rn2):
    from mocdp.comp.connection import Connection
    def translate_connections(c):
        if c.dp1 == name and c.s1 == rn:
            c = Connection(name, rn2, c.dp2, c.s2)
        return c
    connections = map(translate_connections, connections)
    name2dp[name] = wrap_change_name_resource(name2dp[name], rn, rn2)
    return dpgraph_making_sure_no_reps(name2dp, newfunctions, newresources, connections)

def wrap_change_name_resource(ndp, rn, rn2):
    from mocdp.dp.dp_identity import Identity
    from mocdp.comp.wrap import dpwrap
    from mocdp.comp.connection import Connection

    R = ndp.get_rtype(rn)
    second = dpwrap(Identity(R), rn, rn2)
    from mocdp.comp.connection import connect2
    connections = set([Connection('-', rn, '-', rn)])
    return connect2(ndp, second, connections, split=[])

def dpgraph_translate_fn(name2dp, newfunctions, newresources, connections,
                         name, fn, fn2):
    from mocdp.comp.connection import Connection
    def translate_connections(c):
        if c.dp2 == name and c.s2 == fn:
            c = Connection(c.dp1, c.s1, name, fn2)
        return c
    connections = map(translate_connections, connections)
    name2dp[name] = wrap_change_name_function(name2dp[name], fn, fn2)
    return dpgraph_making_sure_no_reps(name2dp, newfunctions, newresources, connections)


def wrap_change_name_function(ndp, fn, fn2):
    from mocdp.dp.dp_identity import Identity
    from mocdp.comp.wrap import dpwrap
    from mocdp.comp.connection import Connection

    F = ndp.get_ftype(fn)
    first = dpwrap(Identity(F), fn2, fn)
    from mocdp.comp.connection import connect2
    connections = set([Connection('-', fn, '-', fn)])
    return connect2(first, ndp, connections, split=[])


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
