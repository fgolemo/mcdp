# -*- coding: utf-8 -*-
from mocdp.comp.context import Connection

__all__ = [
    'compmake_context',
]

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
