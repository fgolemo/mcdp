from contracts import contract
from mocdp.comp.wrap import SimpleWrap
from mcdp_posets.poset_product import PosetProduct
from mocdp.comp.composite import CompositeNamedDP

def cndp_templatize_children(cndp):
    """ Replaces all sub composites with the corresponding template """

    fnames = cndp.get_fnames()
    rnames = cndp.get_rnames()
    connections = cndp.get_connections()

    def filter_child(child):
        if isinstance(child, CompositeNamedDP):
            return ndp_templatize(child)
        else:
            return child

    name2ndp = dict([(k, filter_child(v)) for k, v in cndp.get_name2ndp().items()])

    return CompositeNamedDP.from_parts(name2ndp, connections, fnames, rnames)

@contract(ndp=CompositeNamedDP, returns=SimpleWrap)
def ndp_templatize(ndp):
    """ Creates a template based on the interface. """
    fnames = ndp.get_fnames()
    ftypes = ndp.get_ftypes(fnames)
    rnames = ndp.get_rnames()
    rtypes = ndp.get_rtypes(rnames)

    if len(fnames) == 1:
        fnames = fnames[0]
        F = ftypes[0]
    else:
        F = PosetProduct(tuple(ftypes))

    if len(rnames) == 1:
        rnames = rnames[0]
        R = rtypes[0]
    else:
        R = PosetProduct(tuple(rtypes))

    from mocdp.comp.template_imp import Dummy

    dp = Dummy(F, R)
    res = SimpleWrap(dp, fnames, rnames)
    return res
