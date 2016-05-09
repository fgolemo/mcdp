from mocdp.comp.composite import CompositeNamedDP
from contracts import contract
from mocdp.comp.context import Connection, get_name_for_fun_node, \
    get_name_for_res_node
from contracts.utils import raise_desc
from mocdp.comp.wrap import SimpleWrap

def add_prefix(ndp, prefix):
    if isinstance(ndp, SimpleWrap):
        dp = ndp.get_dp()
        fnames = ['%s_%s' % (prefix, _) for _ in ndp.get_fnames()]
        rnames = ['%s_%s' % (prefix, _) for _ in ndp.get_rnames()]
        icon = ndp.icon
        if len(fnames) == 1: fnames = fnames[0]
        if len(rnames) == 1: rnames = rnames[0]
        sw = SimpleWrap(dp, fnames=fnames, rnames=rnames, icon=icon)
        print sw
        return sw
    

    if isinstance(ndp, CompositeNamedDP):
        def get_new_name(name2):
            #return '_fun_%s' % name
            if '_fun_' in name2:
                fname = name2[len('_fun_'):]
                return get_name_for_fun_node('%s_%s' % (prefix, fname))
            elif '_res_' in name2:
                rname = name2[len('_res_'):]
                return get_name_for_res_node('%s_%s' % (prefix, rname))
            else:
                return "%s_%s" % (prefix, name2)

        names2 = {}
        connections2 = set()
        for name2, ndp2 in ndp.get_name2ndp().items():
            _ = get_new_name(name2)
            assert not _ in names2
            names2[_] = ndp2
        
        for c in ndp.get_connections():
            dp1, s1, dp2, s2 = c.dp1, c.s1, c.dp2, c.s2
            dp1 = get_new_name(dp1)
            dp2 = get_new_name(dp2)
            assert s1 in names2[dp1].get_rnames() 
            assert s2 in names2[dp2].get_fnames()
            c2 = Connection(dp1=dp1, s1=s1, dp2=dp2, s2=s2)
            connections2.add(c2)
            
        fnames2 = ['%s_%s' % (prefix, _) for _ in ndp.get_fnames()]
        rnames2 = ['%s_%s' % (prefix, _) for _ in ndp.get_rnames()]
        return CompositeNamedDP.from_parts(names2, connections2, fnames2, rnames2)
    assert False
    
@contract(ndp=CompositeNamedDP)
def flatten_composite(ndp):
    name2ndp = ndp.get_name2ndp()
    connections = ndp.get_connections()
    fnames = ndp.get_fnames()
    rnames = ndp.get_rnames()
    names2 = {}
    connections2 = set()

    for name, n0 in name2ndp.items():
        n1 = n0.flatten()
        nn = add_prefix(n1, prefix=name)
        for x in nn.get_fnames():
            assert name in x
        for x in nn.get_rnames():
            assert name in x

        if isinstance(nn, CompositeNamedDP):
            
#             def get_new_name(name2):
#                 return "%s_%s" % (name, name2)
#
            for name2, ndp2 in nn.get_name2ndp().items():
#                 _ = get_new_name(name2)
                assert not name2 in names2
                names2[name2] = ndp2
            
            for c in nn.get_connections():
                dp1, s1, dp2, s2 = c.dp1, c.s1, c.dp2, c.s2
#                 dp1 = get_new_name(dp1)
#                 dp2 = get_new_name(dp2)

                assert s1 in names2[dp1].get_rnames()
                assert s2 in names2[dp2].get_fnames()
                c2 = Connection(dp1=dp1, s1=s1, dp2=dp2, s2=s2)
                connections2.add(c2)
        else:
            names2[name] = nn

    for c in connections:
        dp2 = c.dp2
        s2 = c.s2
        dp1 = c.dp1
        s1 = c.s1

        dp2_was_exploded = isinstance(name2ndp[dp2], CompositeNamedDP)
        if dp2_was_exploded:
            dp2_ = "_fun_%s_%s" % (dp2, s2)
            if not dp2_ in names2:
                raise_desc(AssertionError, "?", dp2_=dp2_, c=c, names2=sorted(names2))
        else:
            dp2_ = dp2

        dp1_was_exploded = isinstance(name2ndp[dp1], CompositeNamedDP)
        if dp1_was_exploded:
            dp1_ = "_res_%s_%s" % (dp1, s1)
            if not dp1_ in names2:
                raise_desc(AssertionError, "?", dp1_=dp1_, c=c, names2=sorted(names2))
        else:
            dp1_ = dp1
        print('name2ndp: %s' % list(name2ndp))
        print(c)
        s1_ = '%s_%s' % (dp1_, s1)

        assert dp1_ in names2
        print('s1: %s' % s1_)
        print('dp1_: %s' % dp1_)
        print(names2[dp1_])
        assert s1_ in names2[dp1_].get_rnames() , (s1_, names2[dp1_].get_rnames())

        s2_ = '%s_%s' % (dp2_, s2)
        assert dp2_ in names2
        assert s2_ in names2[dp2_].get_fnames(), (s2_, names2[dp2_].get_fnames())

        c2 = Connection(dp1=dp1_, s1=s1_, dp2=dp2_, s2=s2_)
        # (dp2, s2)
        connections2.add(c2)


    # Connection0 = namedtuple('Connection', 'dp1 s1 dp2 s2')
    # class Connection(Connection0):

    return CompositeNamedDP.from_parts(names2, connections2, fnames, rnames)
