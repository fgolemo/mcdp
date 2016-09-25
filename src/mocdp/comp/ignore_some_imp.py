from contracts import contract
from contracts.utils import check_isinstance, raise_desc
from mcdp_dp import Constant, LimitMaximals
from mocdp.comp.composite import CompositeNamedDP
from mocdp.comp.context import Connection, Context
from mocdp.comp.interfaces import NamedDP
from mocdp.comp.wrap import dpwrap


__all__ = [
    'IgnoreSome',
]

@contract(ndp=NamedDP, returns=CompositeNamedDP)
def ignore_some(ndp, ignore_fnames, ignore_rnames):
    """ Ignores some functionalities or resources """
    fnames0 = ndp.get_fnames()
    rnames0 = ndp.get_rnames()
    for fname in ignore_fnames:
        check_isinstance(fname, str)
        if not fname in fnames0:
            msg = 'Could not find functionality %r in %r.' % (fname, fnames0)
            raise_desc(ValueError, msg, fname=fname, fnames=fnames0)
    for rname in ignore_rnames:
        check_isinstance(rname, str)
        if not rname in rnames0:
            msg = 'Could not find resource %r in %r.' % (rname, rnames0)
            raise_desc(ValueError, msg, rname=rname, rnames=rnames0)

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

