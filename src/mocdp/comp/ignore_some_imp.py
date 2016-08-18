from mocdp.comp.composite import CompositeNamedDP
from contracts import contract
from mocdp.comp.interfaces import NamedDP
from mocdp.comp.context import Context, Connection
from mcdp_dp.dp_constant import Constant
from mocdp.comp.wrap import dpwrap
from mcdp_dp.dp_limit import LimitMaximals

__all__ = [
    'IgnoreSome',
]

@contract(ndp=NamedDP, returns=CompositeNamedDP)
def ignore_some(ndp, ignore_fnames, ignore_rnames):
    """ Ignores some functionalities or resources """
    c = Context()
    orig = '_orig'
    c.add_ndp(orig, ndp)

    for fname in ndp.get_fnames():
        F = ndp.get_ftype(fname)

        if fname in ignore_fnames:
            dp = Constant(F, F.get_bottom())
            n = '_const_f_%s' % fname
            c.add_ndp(n, dpwrap(dp, [], fname))
        else:
            n = c.add_ndp_fun_node(fname, F)
        con = Connection(n, fname, orig, fname)
        c.add_connection(con)


    for rname in ndp.get_rnames():
        R = ndp.get_rtype(rname)

        if rname in ignore_rnames:
            dp = LimitMaximals(R, R.get_maximal_elements())
            n = '_const_r_%s' % rname
            c.add_ndp(n, dpwrap(dp, rname, []))
        else:
            n = c.add_ndp_res_node(rname, R)
        con = Connection(orig, rname, n, rname)
        c.add_connection(con)

    return CompositeNamedDP.from_context(c)

