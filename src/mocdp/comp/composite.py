from .interfaces import NamedDP
from contracts.utils import format_dict_long, format_list_long, raise_wrapped
from mocdp.comp.context import Connection
from mocdp.comp.interfaces import NotConnected
from mocdp.exceptions import DPSemanticError


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
        self.context = context
        self._rnames = list(self.context.rnames)
        self._fnames = list(self.context.fnames)

    def check_fully_connected(self):
        for name, ndp in self.context.names.items():
            try:
                ndp.check_fully_connected()
            except NotConnected as e:
                msg = 'Sub-design problem %r is not connected.' % name
                raise_wrapped(NotConnected, e, msg, compact=True)
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
        ndp = self.context.get_ndp_res(rn)
        return ndp.get_rtype(ndp.get_rnames()[0])

    def get_ftype(self, fn):
        ndp = self.context.get_ndp_fun(fn)
        return ndp.get_ftype(ndp.get_fnames()[0])

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
        context = compact_context(self.context)
        return CompositeNamedDP(context)


def compact_context(context):
    from .context_functions import find_nodes_with_multiple_connections
    from mocdp.dp.dp_flatten import Mux
    from mocdp.comp.wrap import dpwrap

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
        # demux = Mux(PosetProduct((R,)), [(0, 0), (0, 1)])
        from mocdp.dp.dp_identity import Identity
        demux = Identity(R)
        demuxndp = dpwrap(demux, sname, s2s)

        from mocdp.comp.connection import connect2

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
