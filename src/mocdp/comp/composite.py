# -*- coding: utf-8 -*-
import sys

from contracts import contract
from contracts.utils import (format_dict_long, format_list_long, raise_desc,
    raise_wrapped)
from mcdp_dp import Mux
from mcdp_posets import NotEqual, PosetProduct
from mocdp import ATTR_LOAD_NAME
from mocdp.comp.context import Context, is_fun_node_name
from mocdp.comp.wrap import SimpleWrap
from mocdp.exceptions import DPSemanticError

from .context import Connection  # @UnusedImport
from .interfaces import NamedDP, NotConnected


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
        self.context = Context()
        self.context.names = context.names.copy()
        self.context.connections = list(context.connections)
        self.context.fnames = list(context.fnames)
        self.context.rnames = list(context.rnames)

        check_consistent_data(self.context.names, self.context.fnames,
                              self.context.rnames, self.context.connections)


        self._rnames = list(self.context.rnames)
        self._fnames = list(self.context.fnames)

    def __copy__(self):
        c = Context()
        c.names = dict(**self.context.names)
        c.connections = list(self.context.connections)
        c.fnames = list(self.context.fnames)
        c.rnames = list(self.context.rnames)
        return CompositeNamedDP(c)

    @staticmethod
    def from_context(context):
        return CompositeNamedDP(context)

    @staticmethod
    def from_parts(name2ndp, connections, fnames, rnames):
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
        from mcdp_lang.blocks import check_missing_connections
        check_missing_connections(self.context)

    def compact(self):
        """ Each set of edges that share both tail and head
            are replaced by their product. """ 
        from mocdp.comp.composite_compact import compact_context
        context = compact_context(self.context)
        return CompositeNamedDP(context)

    def flatten(self):
        from mocdp.comp.flattening.flatten import cndp_flatten
        return cndp_flatten(self)

    def templatize_children(self):
        from .composite_templatize import cndp_templatize_children
        return cndp_templatize_children(self)

    def abstract(self):
        if not self.context.names:
            # this means that there are nor children, nor functions nor resources
            dp = Mux(PosetProduct(()), ())
            ndp = SimpleWrap(dp, fnames=[], rnames=[])
            return ndp

        try:
            self.check_fully_connected()
        except NotConnected as e:
            msg = 'Cannot abstract because not all subproblems are connected.'
            raise_wrapped(DPSemanticError, e, msg, exc=sys.exc_info(), compact=True)

        from mocdp.comp.composite_abstraction import cndp_abstract
        res = cndp_abstract(self)
        assert isinstance(res, SimpleWrap), type(res)

        assert res.get_fnames() == self.context.fnames
        assert res.get_rnames() == self.context.rnames
        
        return res

    def get_dp(self):
        ndp = self.abstract()
        dp = ndp.get_dp()
        return dp

    def __repr__(self):
        s = 'CompositeNDP'

        if hasattr(self, ATTR_LOAD_NAME):
            s += '\n (loaded as %r)' % getattr(self, ATTR_LOAD_NAME)
#         if hasattr(self, ATTRIBUTE_NDP_RECURSIVE_NAME):
#             s += '\n (labeled as %s)' % getattr(self, ATTRIBUTE_NDP_RECURSIVE_NAME).__str__()
        for f in self._fnames:
            s += '\n provides %s  [%s]' % (f, self.get_ftype(f))
        for r in self._rnames:
            s += '\n requires %s  [%s]' % (r, self.get_rtype(r))

        s += '\n %d nodes, %d edges' % (len(self.context.names), len(self.context.connections))

        s += '\n connections: \n' + format_list_long(self.context.connections, informal=True)
        s += '\n names: \n' + format_dict_long(self.context.names, informal=True)
        return s


def check_good_name(n):
    """ Checks that n is a good name for a node """
    if ' ' in n:
        raise_desc(ValueError, "Invalid name", n=n)


def check_consistent_data(names, fnames, rnames, connections):
    from mocdp.comp.context import get_name_for_res_node, get_name_for_fun_node
    from mocdp.comp.context import is_res_node_name
    from mcdp_posets.types_universe import get_types_universe
    tu = get_types_universe()

    for n in names:
        try:
            check_good_name(n)
        except ValueError as e:
            msg = 'This name is not good.'
            raise_wrapped(ValueError, e, msg, names=names)

        isit, x = is_fun_node_name(n)
        if isit and not x in fnames:
            msg = 'The name for the node seems to be the one for a function.'
            raise_desc(ValueError, msg, n=n, fnames=fnames)

        isit, x = is_res_node_name(n)
        if isit and not x in rnames:
            if not n in rnames:
                msg = 'The name for the node seems to be the one for a resource.'
                raise_desc(ValueError, msg, n=n, rnames=rnames)

    for f in  fnames:
        fnode = get_name_for_fun_node(f)
        if not fnode in names:
            msg = 'Expecting to see a node with the name of the function.'
            raise_desc(ValueError, msg, f=f, names=list(names.keys()))

        fn = names[fnode]
        if not f in fn.get_fnames():
            msg = ('Expecting to see the special function node have function '
                   'with function name.')
            raise_desc(ValueError, msg, f=f, fnode=fnode, fn=fn,
                        fn_fnames=fn.get_fnames())

    for r in  rnames:
        rnode = get_name_for_res_node(r)
        if not rnode in names:
            msg = 'Expecting to see a node with the name of the resource.'
            raise_desc(ValueError, msg, r=r, names=list(names.keys()))

        rn = names[rnode]
        if not r in rn.get_rnames():
            msg = ('Expecting to see the special resource node have resource '
                   'with resource name.')
            raise_desc(ValueError, msg, r=r, rnode=rnode, rn=rn,
                       rn_rnames=rn.get_rnames())


    for c in connections:
        try:
            if not c.dp1 in names:
                raise_desc(ValueError, 'First DP not found.', name=c.dp1,
                           available=list(names))

            if not c.s1 in names[c.dp1].get_rnames():
                raise_desc(ValueError, 'Resource not found',
                           rname=c.s1, available=names[c.dp1].get_rnames())

            if not c.dp2 in names:
                raise_desc(ValueError, 'Second DP not found.', name=c.dp2,
                           available=list(names))

            if not c.s2 in names[c.dp2].get_fnames():
                raise_desc(ValueError, 'Function not found.',
                           s2=c.s2, available=names[c.dp2].get_fnames())

            R = names[c.dp1].get_rtype(c.s1)
            F = names[c.dp2].get_ftype(c.s2)

            try:
                tu.check_equal(R, F)
            except NotEqual as e:
                msg = 'Invalid connection %s' % c.__repr__()
                raise_wrapped(ValueError, e, msg, R=R, F=F)


        except ValueError as e:
            msg = 'Invalid connection'
            raise_wrapped(ValueError, e, msg, c=c, names=list(names))

@contract(cndp=CompositeNamedDP, returns='list(tuple(str, $NamedDP))')
def cndp_iterate_res_nodes(cndp):
    res = []
    from mocdp.comp.context import is_res_node_name

    for name2, ndp2 in cndp.get_name2ndp().items():
        isitr, rname = is_res_node_name(name2)
        if isitr:
            res.append((rname, ndp2))
    return res


@contract(cndp=CompositeNamedDP, returns='list(tuple(str, $NamedDP))')
def cndp_iterate_fun_nodes(cndp):
    res = []
    for name2, ndp2 in cndp.get_name2ndp().items():
        isitr, fname = is_fun_node_name(name2)
        if isitr:
            res.append((fname, ndp2))
    return res



@contract(cndp=CompositeNamedDP, returns='list(tuple(str, $NamedDP))')
def cndp_get_name_ndp_notfunres(cndp):
    """ Yields a sequence of (name, ndp) excluding 
        the fake ones that represent function or resource. """
    assert isinstance(cndp, CompositeNamedDP)
    from mocdp.comp.context import is_res_node_name

    res = []
    for name2, ndp2 in cndp.get_name2ndp().items():
        isitf, _ = is_fun_node_name(name2)
        isitr, _ = is_res_node_name(name2)
        if isitf or isitr:
            # do not add the identity nodes
            # that represent functions or resources
            continue
        else:
            res.append((name2, ndp2))
    return res
