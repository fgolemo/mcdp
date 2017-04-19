# -*- coding: utf-8 -*-
from mocdp.comp.wrap import SimpleWrap
from mcdp.exceptions import mcdp_dev_warning


def eval_ndp_approx_lower(r, context):
    from mcdp_lang.eval_ndp_imp import eval_ndp
    from mcdp_dp.dp_transformations import get_dp_bounds

    nl = r.level
    ndp = eval_ndp(r.ndp, context)
    dp = ndp.get_dp()
    mcdp_dev_warning('make it better')
    dpl, _ = get_dp_bounds(dp, nl, 1)

    fnames = ndp.get_fnames()
    rnames = ndp.get_rnames()
    rnames = rnames if len(rnames) > 1 else rnames[0]
    fnames = fnames if len(fnames) > 1 else fnames[0]
    ndp2 = SimpleWrap(dpl, fnames, rnames)
    return ndp2


def eval_ndp_approx_upper(r, context):
    from mcdp_lang.eval_ndp_imp import eval_ndp
    from mcdp_dp.dp_transformations import get_dp_bounds

    nu = r.level
    ndp = eval_ndp(r.ndp, context)
    dp = ndp.get_dp()
    mcdp_dev_warning('make it better')
    _, dpu = get_dp_bounds(dp, 1, nu)

    fnames = ndp.get_fnames()
    rnames = ndp.get_rnames()
    rnames = rnames if len(rnames) > 1 else rnames[0]
    fnames = fnames if len(fnames) > 1 else fnames[0]
    ndp2 = SimpleWrap(dpu, fnames, rnames)
    return ndp2
