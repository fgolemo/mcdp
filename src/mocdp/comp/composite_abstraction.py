# -*- coding: utf-8 -*-
from networkx.algorithms.cycles import simple_cycles

from contracts import contract
from contracts.utils import raise_desc
from mcdp_dp import DPLoop2, Mux
from mcdp_dp.dp_series_simplification import make_series
from mcdp_posets import PosetProduct, get_types_universe
from mcdp import logger
from mocdp.comp.composite import CompositeNamedDP
from mocdp.comp.context_functions import dpgraph_making_sure_no_reps
from mocdp.comp.wrap import SimpleWrap
from mcdp.exceptions import mcdp_dev_warning


@contract(ndp=CompositeNamedDP, returns=SimpleWrap)
def cndp_abstract(ndp):
    from .connection import get_connection_multigraph
    
    G = get_connection_multigraph(ndp.get_connections())
    cycles = list(simple_cycles(G))
    if len(cycles) > 0:
        logger.debug('cndp_abstract: %d cycles' % len(cycles))
    if not cycles:
        return dpgraph_making_sure_no_reps(ndp.context)
    else:
        return cndp_abstract_loop2(ndp)


@contract(ndp=CompositeNamedDP, returns=SimpleWrap)
def cndp_abstract_loop2(ndp):
    """ Abstracts the dp using the canonical form """
    from .composite_makecanonical import get_canonical_elements

    res = get_canonical_elements(ndp)

    cycles = res['cycles']
    if len(cycles) > 1:
        msg = ('I expected that the cycles were already compacted, while %s remain.' %
               cycles)
        raise_desc(NotImplementedError, msg, res=res)

    inner = res['inner']

    inner_dp = inner.get_dp()

    extraf = res['extraf']
    extrar = res['extrar']

    # print 'ndp', ndp.get_fnames(), ndp.get_rnames()
    # print 'inner', inner.get_fnames(), inner.get_rnames()
    # print 'extra', extraf, extrar
    # print 'cycles', res['cycles']
    assert extraf == ndp.get_fnames(), (extraf, ndp.get_fnames())
    assert extrar == ndp.get_rnames(), (extrar, ndp.get_rnames())

    # We use the ndp layer to create a dp that has 
    
    F1 = ndp.get_ftypes(extraf)
    R1 = ndp.get_rtypes(extrar)
    
#     if len(cycles) > 1:
#         msg = 'Expected there would be at most one cycle, found: %d.' % len(cycles)
#         raise_desc(Exception, msg, ndp=ndp)

    if len(cycles) == 0:
        # raise NotImplementedError()
        mcdp_dev_warning('this needs much more testing')
        dp = inner_dp
        fnames = extraf
        rnames = extrar
        if len(fnames) == 1:
            fnames = fnames[0]
        if len(rnames) == 1:
            rnames = rnames[0]
        from mocdp.comp.wrap import dpwrap
        return dpwrap(dp, fnames, rnames)

    F2 = inner.get_rtype(cycles[0])
    R2 = F2
    
    dp0F = PosetProduct((F1,F2))
    
    coords1 = []
    for inner_fname in inner.get_fnames():
        if inner_fname in extraf:
            coords1.append((0, extraf.index(inner_fname)))
        else:
            coords1.append(1)
    if len(coords1) == 1:
        coords1 = coords1[0]
    mux1 = Mux(dp0F, coords1)

    assert mux1.get_res_space() == inner_dp.get_fun_space()

    mux0F = inner_dp.get_res_space()
    coords2extra = []
    for rname in extrar:
        i = inner.get_rnames().index(rname)
        if len(inner.get_rnames()) == 1:
            i = ()
        coords2extra.append(i)
    
    j = inner.get_rnames().index(cycles[0])
    if len(inner.get_rnames()) == 1:
        j = ()
    coords2 = [coords2extra, j]
        
    mux2 = Mux(mux0F, coords2)

    dp0 = make_series(make_series(mux1, inner_dp), mux2)
    dp0R_expect = PosetProduct((R1, R2))
    assert dp0.get_res_space() == dp0R_expect

    dp = DPLoop2(dp0)

    # this is what we want to obtain at the end
    F = ndp.get_ftypes(ndp.get_fnames())
    if len(ndp.get_fnames()) == 1:
        F = F[0]
    R = ndp.get_rtypes(ndp.get_rnames())
    if len(ndp.get_rnames()) == 1:
        R = R[0]

    if len(extraf) == 1:
        dp = make_series(Mux(F, [()]), dp)
    if len(extrar) == 1:
        dp = make_series(dp, Mux(PosetProduct((R,)), 0))

    tu = get_types_universe()
    tu.check_equal(dp.get_fun_space(), F)
    tu.check_equal(dp.get_res_space(), R)

    fnames = extraf
    rnames = extrar
    if len(fnames) == 1:
        fnames = fnames[0]
    if len(rnames) == 1:
        rnames = rnames[0]
    # now dp has extra (1) and (1)
    return SimpleWrap(dp, fnames=fnames, rnames=rnames)

