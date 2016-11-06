# -*- coding: utf-8 -*-
from _collections import defaultdict

from contracts import contract
from contracts.utils import check_isinstance, raise_desc
from mcdp_dp import Identity
from mocdp.comp.composite import CompositeNamedDP
from mocdp.comp.context import (Connection, get_name_for_fun_node,
    get_name_for_res_node, is_fun_node_name, is_res_node_name)
from mocdp.comp.labelers import LabelerNDP
from mocdp.comp.simplify_identities_imp import simplify_identities
from mocdp.comp.wrap import SimpleWrap
from mocdp.ndp.named_coproduct import NamedDPCoproduct


__all__ = [
    'cndp_flatten',
    'flatten_add_prefix',
]

sep = '/'

def flatten_add_prefix(ndp, prefix):
    """ Adds a prefix for every node name and to functions/resources. """

    if isinstance(ndp, SimpleWrap):
        dp = ndp.get_dp()
        fnames = ['%s%s%s' % (prefix, sep, _) for _ in ndp.get_fnames()]
        rnames = ['%s%s%s' % (prefix, sep, _) for _ in ndp.get_rnames()]
        icon = ndp.icon
        if len(fnames) == 1: fnames = fnames[0]
        if len(rnames) == 1: rnames = rnames[0]
        sw = SimpleWrap(dp, fnames=fnames, rnames=rnames, icon=icon)
        return sw
    
    if isinstance(ndp, CompositeNamedDP):
        
        def get_new_name(name2):
            isf, fname = is_fun_node_name(name2)
            isr, rname = is_res_node_name(name2)

            if isf:
                return get_name_for_fun_node('%s%s%s' % (prefix, sep, fname))
            elif isr:
                return get_name_for_res_node('%s%s%s' % (prefix, sep, rname))
            else:
                return "%s%s%s" % (prefix, sep, name2)
            
        def transform(name2, ndp2):
            # Returns name, ndp
            isf, fname = is_fun_node_name(name2)
            isr, rname = is_res_node_name(name2)
            
            if isf or isr:

                if isinstance(ndp2, SimpleWrap):

                    if isf:
                        fnames = "%s%s%s" % (prefix, sep, fname)
                        rnames = "%s%s%s" % (prefix, sep, fname)
                    if isr:
                        fnames = "%s%s%s" % (prefix, sep, rname)
                        rnames = "%s%s%s" % (prefix, sep, rname)

                    dp = ndp2.dp
                    res = SimpleWrap(dp=dp, fnames=fnames, rnames=rnames)

                elif isinstance(ndp2, LabelerNDP):
                    ndp_inside = transform(name2, ndp2.ndp)
                    return LabelerNDP(ndp_inside, ndp2.recursive_name)
                else:
                    raise NotImplementedError(type(ndp2))

            else:
                res = flatten_add_prefix(ndp2, prefix)

            return res


        names2 = {}
        connections2 = set()
        for name2, ndp2 in ndp.get_name2ndp().items():
            name_ = get_new_name(name2)
            ndp_ = transform(name2, ndp2)
            assert not name_ in names2
            names2[name_] = ndp_
        
        for c in ndp.get_connections():
            dp1, s1, dp2, s2 = c.dp1, c.s1, c.dp2, c.s2
            dp1 = get_new_name(dp1)
            dp2 = get_new_name(dp2)
            s1_ = "%s%s%s" % (prefix, sep, s1)
            s2_ = "%s%s%s" % (prefix, sep, s2)
            assert s1_ in names2[dp1].get_rnames(), (s1_, names2[dp1].get_rnames())
            assert s2_ in names2[dp2].get_fnames(), (s2_, names2[dp1].get_fnames())
            c2 = Connection(dp1=dp1, s1=s1_, dp2=dp2, s2=s2_)
            connections2.add(c2)
            
        fnames2 = ['%s%s%s' % (prefix, sep, _) for _ in ndp.get_fnames()]
        rnames2 = ['%s%s%s' % (prefix, sep, _) for _ in ndp.get_rnames()]

        return CompositeNamedDP.from_parts(names2, connections2, fnames2, rnames2)

    if isinstance(ndp, NamedDPCoproduct):
        children = ndp.ndps
        children2 = tuple([flatten_add_prefix(_, prefix) for _ in children])
        labels2 = ndp.labels
        return NamedDPCoproduct(children2, labels2)

    if isinstance(ndp, LabelerNDP):
        x = flatten_add_prefix(ndp.ndp, prefix)
        return LabelerNDP(x, ndp.recursive_name)

    assert False, type(ndp)
    
@contract(ndp=CompositeNamedDP)
def cndp_flatten(ndp):
    check_isinstance(ndp, CompositeNamedDP)

    name2ndp = ndp.get_name2ndp()
    connections = ndp.get_connections()
    fnames = ndp.get_fnames()
    rnames = ndp.get_rnames()

    names2 = {}
    connections2 = []

    proxy_functions = defaultdict(lambda: dict())  # proxy[name][fname]
    proxy_resources = defaultdict(lambda: dict())

    for name, n0 in name2ndp.items():
        # add empty (in case they have no functions/resources)
        proxy_functions[name] = {}
        proxy_resources[name] = {}

        n1 = n0.flatten()

        if isinstance(n1, CompositeNamedDP):
            nn = flatten_add_prefix(n1, prefix=name)
        else:
            nn = n1

        if isinstance(nn, CompositeNamedDP):
#             nn_connections = nn.get_connections()
            for name2, ndp2 in nn.get_name2ndp().items():
                assert not name2 in names2
                isitf, is_fname = is_fun_node_name(name2)
                isitr, is_rname = is_res_node_name(name2)

                if (isitf or isitr):
                    # connected_to_something = is_dp_connected(name2, nn_connections)
                    # do not add the identity nodes
                    # that represent functions or resources
                    # except if they are unconnected

                    # add_identities = not connected_to_something
                    add_identities = True

                    if not add_identities:
                        continue
                    else:
                        # think of the case where there are a f and r with
                        # same name
                        if isitf:
                            use_name = is_fname + '_f'
                        if isitr:
                            use_name = is_rname + '_r'

                        assert not use_name in names2, use_name
                        names2[use_name] = ndp2

                        if isitf:
                            proxy_functions[name][is_fname] = (use_name, ndp2.get_fnames()[0])

                        if isitr:
                            proxy_resources[name][is_rname] = (use_name, ndp2.get_rnames()[0])

                else:
                    assert not name2 in names2
                    names2[name2] = ndp2
            
            for c in nn.get_connections():
                # is it a connection to a function

                if False:
                    isitf, fn = is_fun_node_name(c.dp1)
                    isitr, rn = is_res_node_name(c.dp2)

                    if isitf and isitr:
                        # This is the case where there is a straight connection
                        # from function to resource:
                        #
                        # f = instance mcdp {
                        #     provides a [R]
                        #     requires c [R]
                        #
                        #     c >= a
                        # }
                        # In this case, we need to add an identity
                        new_name = '_%s_pass_through_%s' % (name, c.s2)
                        F = nn.get_name2ndp()[c.dp1].get_ftype(c.s1)
                        ndp_pass = SimpleWrap(Identity(F), fnames=fn, rnames=rn)
                        assert not new_name in names2
                        names2[new_name] = ndp_pass
                        proxy_functions[name][fn] = (new_name, fn)
                        proxy_resources[name][rn] = (new_name, rn)
                        continue

                    if isitf:
                        proxy_functions[name][fn] = (c.dp2, c.s2)
                        continue

                    if isitr:
                        proxy_resources[name][rn] = (c.dp1, c.s1)
                        continue

                isitf, fn = is_fun_node_name(c.dp1)
                if isitf:
                    dp1 = fn + '_f'
                    assert dp1 in names2
                else:
                    dp1 = c.dp1

                isitr, rn = is_res_node_name(c.dp2)
                if isitr:
                    dp2 = rn + '_r'
                    assert dp2 in names2
                else:
                    dp2 = c.dp2

                assert dp1 in names2
                assert dp2 in names2
                assert c.s1 in names2[dp1].get_rnames()
                assert c.s2 in names2[dp2].get_fnames()
                c2 = Connection(dp1=dp1, s1=c.s1, dp2=dp2, s2=c.s2)
                connections2.append(c2)
        else:
            for fn in nn.get_fnames():
                proxy_functions[name][fn] = (name, fn)

            for rn in nn.get_rnames():
                proxy_resources[name][rn] = (name, rn)

            assert not name in names2
            names2[name] = nn

    # check that these were correctly generated:
    #  proxy_functions
    #  proxy_resources
    def exploded(name):
        return isinstance(name2ndp[name], CompositeNamedDP)
    # print list(proxy_resources)
    errors = []
    for name, n0 in name2ndp.items():
        try:

            assert name in proxy_functions, name
            assert name in proxy_resources
            if exploded(name):
                for fname in n0.get_fnames():
                    newfname = "%s/%s" % (name, fname)
                    assert newfname in proxy_functions[name], (newfname, proxy_functions[name])
                for rname in n0.get_rnames():
                    newrname = "%s/%s" % (name, rname)
                    assert newrname in proxy_resources[name], (newrname, proxy_resources[name])
            else:
                for fname in n0.get_fnames():
                    assert fname in proxy_functions[name], (fname, proxy_functions[name])
                for rname in n0.get_rnames():
                    assert rname in proxy_resources[name]
        except Exception as e:
            s = '%s:\n %s %s \n\n%s' % (name, proxy_resources[name], proxy_functions[name], e)
            errors.append(s)
    if errors:
        s = "\n\n".join(errors)
        s += '%s %s' % (proxy_resources, proxy_functions)
        raise Exception(s)

    for c in connections:
        dp2 = c.dp2
        s2 = c.s2
        dp1 = c.dp1
        s1 = c.s1

        dp2_was_exploded = isinstance(name2ndp[dp2], CompositeNamedDP)
        if dp2_was_exploded:
            if not dp2 in proxy_functions:
                msg = 'Bug: cannot find dp2.'
                raise_desc(Exception, msg, dp2=dp2, keys=list(proxy_functions),
                           c=c)

            (dp2_, s2_) = proxy_functions[dp2]["%s/%s" % (dp2, s2)]
#
#             dp2_ = "_fun_%s%s%s" % (dp2, sep, s2)
            if not dp2_ in names2:
                raise_desc(AssertionError, "?", dp2_=dp2_, c=c, names2=sorted(names2))
#             s2_ = '%s%s%s' % (dp2, sep, s2)
        else:
            dp2_ = dp2
            s2_ = s2

        dp1_was_exploded = isinstance(name2ndp[dp1], CompositeNamedDP)
        if dp1_was_exploded:
            (dp1_, s1_) = proxy_resources[dp1]["%s/%s" % (dp1, s1)]
#
#             dp1_ = "_res_%s%s%s" % (dp1, sep, s1)
#             if not dp1_ in names2:
#                 raise_desc(AssertionError, "?", dp1_=dp1_, c=c, names2=sorted(names2))
#             s1_ = '%s%s%s' % (dp1, sep, s1)
        else:
            dp1_ = dp1
            s1_ = s1

        assert dp1_ in names2

        assert s1_ in names2[dp1_].get_rnames() , (s1_, names2[dp1_].get_rnames())

        assert dp2_ in names2
        assert s2_ in names2[dp2_].get_fnames(), (s2_, names2[dp2_].get_fnames())

        c2 = Connection(dp1=dp1_, s1=s1_, dp2=dp2_, s2=s2_) 
        connections2.append(c2)

    ndp_res = CompositeNamedDP.from_parts(names2, connections2, fnames, rnames)

    ndp_simplified = simplify_identities(ndp_res)
    return ndp_simplified
