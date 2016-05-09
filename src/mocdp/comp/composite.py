# -*- coding: utf-8 -*-
from .context import Connection
from .interfaces import NamedDP, NotConnected
from contracts.utils import format_dict_long, format_list_long, raise_wrapped, \
    raise_desc
from mocdp.exceptions import DPSemanticError
from contracts import contract

__all__ = [
    'CompositeNamedDP',
]


class CompositeNamedDP(NamedDP):

    """ 
        The only tricky thing is that if there is only one function,
        then F = F1
        but if there are two,
        then F = PosetProduct((F1, F2))
        
        Same thing with the resources.
    
    """

    def __init__(self, context):
        from mocdp.comp.context import Context
        from mocdp.comp.context import get_name_for_fun_node, get_name_for_res_node

        self.context = Context()
        self.context.names = context.names.copy()
        self.context.connections = list(context.connections)
        self.context.fnames = list(context.fnames)
        self.context.rnames = list(context.rnames)

        names = self.context.names
        for n in names:
            try:
                check_good_name(n)
            except ValueError as e:
                raise_wrapped(ValueError, e, names=names)
        for f in self.context.fnames:
            if not get_name_for_fun_node(f) in  names:
                msg = 'Expecting to see a node with the name of the function.'
                raise_desc(ValueError, msg, f=f, names=list(names.keys()))

        for r in self.context.rnames:
            if not  get_name_for_res_node(r) in  names:
                msg = 'Expecting to see a node with the name of the resource.'
                raise_desc(ValueError, msg, r=r, names=list(names.keys()))

        for c in self.context.connections:
            try:
                if not c.dp1 in names:
                    raise ValueError()

                if not c.s1 in names[c.dp1].get_rnames():
                    raise ValueError()

                if not c.dp2 in names:
                    raise ValueError()

                if not c.s2 in names[c.dp2].get_fnames():
                    raise_desc(ValueError, 'Function not found.',
                               s2=c.s2, rnames=names[c.dp2].get_fnames())

            except ValueError as e:
                msg = 'Invalid connection'
                raise_wrapped(ValueError, e, msg, c=c, names=list(names))

        self._rnames = list(self.context.rnames)
        self._fnames = list(self.context.fnames)

    @staticmethod
    def from_context(context):
        return CompositeNamedDP(context)

    @staticmethod
    def from_parts(name2ndp, connections, fnames, rnames):
        from mocdp.comp.context import Context
        c = Context()
        c.names = name2ndp
        c.connections = connections
        c.fnames = fnames
        c.rnames = rnames
        return CompositeNamedDP(c)

    @contract(returns='dict(str:$NamedDP)')
    def get_name2ndp(self):
        """ Returns the map from name to nodes """
        return self.context.names

    @contract(returns='set($Connection)')
    def get_connections(self):
        return set(self.context.connections)

    @contract(returns='list(str)')
    def get_fnames(self):
        """ Returns list of string """
        return list(self._fnames)

    @contract(returns='list(str)')
    def get_rnames(self):
        """ Returns list of strings """
        return list(self._rnames)

    # accessories

    def get_rtype(self, rn):
        ndp = self.context.get_ndp_res(rn)
        return ndp.get_rtype(ndp.get_rnames()[0])

    def get_ftype(self, fn):
        ndp = self.context.get_ndp_fun(fn)
        return ndp.get_ftype(ndp.get_fnames()[0])

    def check_fully_connected(self):
        for name, ndp in self.context.names.items():
            try:
                ndp.check_fully_connected()
            except NotConnected as e:
                msg = 'Sub-design problem %r is not connected.' % name
                raise_wrapped(NotConnected, e, msg, compact=True)
        from mocdp.lang.blocks import check_missing_connections
        check_missing_connections(self.context)

    # @contract(returns=SimpleWrap)
    def abstract(self):
        try:
            self.check_fully_connected()
        except NotConnected as e:
            msg = 'Cannot abstract because not all subproblems are connected.'
            raise_wrapped(DPSemanticError, e, msg, compact=True)

        from mocdp.comp.context_functions import dpgraph_making_sure_no_reps
        res = dpgraph_making_sure_no_reps(self.context)
        assert res.get_fnames() == self.context.fnames
        assert res.get_rnames() == self.context.rnames
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

    def compact(self):
        # XXX: not sure what this does
        context = compact_context(self.context)
        return CompositeNamedDP(context)

    def flatten(self):
        from mocdp.comp.flatten import flatten_composite
        return flatten_composite(self)

def check_good_name(n):
    """ Checks that n is a good name for a node """
    if ' ' in n:
        raise_desc(ValueError, "Invalid name", n=n)


def compact_context(context):
    from .context_functions import find_nodes_with_multiple_connections
    from mocdp.dp.dp_flatten import Mux
    from mocdp.comp.wrap import dpwrap
    from mocdp.dp.dp_identity import Identity
    from mocdp.comp.connection import connect2

    s = find_nodes_with_multiple_connections(context)
    if not s:
        return context
    else:
        name1, name2, their_connections = s[0]
        print('Will compact %s, %s, %s' % s[0])

        # establish order
        their_connections = list(their_connections)
        s1s = [c.s1 for c in their_connections]
        s2s = [c.s2 for c in their_connections]

        ndp1 = context.names[name1]
        ndp2 = context.names[name2]
        sname = '_'.join(s1s)
        mux = Mux(ndp1.get_rtypes(s1s), [0, 1])
        muxndp = dpwrap(mux, s1s, sname)

        R = mux.get_res_space()

        demux = Identity(R)
        demuxndp = dpwrap(demux, sname, s2s)


        replace1 = connect2(ndp1, muxndp,
                            connections=set([Connection('*', s, '*', s) for s in s1s]),
                            split=[], repeated_ok=False)

        replace2 = connect2(demuxndp, ndp2,
                            connections=set([Connection('*', s, '*', s) for s in s2s]),
                            split=[], repeated_ok=False)

        context.names[name1] = replace1
        context.names[name2] = replace2

        context.connections = [x for x in context.connections
                                    if not x in their_connections]

        c = Connection(name1, sname, name2, sname)
        context.connections.append(c)
        return compact_context(context)
