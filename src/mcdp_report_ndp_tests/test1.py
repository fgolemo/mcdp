# -*- coding: utf-8 -*-
import os

from comptests.registrar import comptest
from contracts import contract
from contracts.utils import raise_desc, raise_wrapped
from mcdp_cli.query_interpretation import convert_string_query
from mcdp_dp import IdentityDP, Mux
from mcdp_dp.dp_transformations import get_dp_bounds
from mcdp_library_tests.tests import get_test_library
from mcdp_posets import NotBelongs, lowerset_project, upperset_project, UpperSet, \
    LowerSet
from mcdp_report.gdc import STYLE_GREENREDSYM
from mcdp_report.gg_ndp import PlottingInfo, gvgen_from_ndp
from mcdp_report.gg_utils import gg_figure
from mocdp.comp.composite import CompositeNamedDP
from mocdp.comp.context import get_name_for_fun_node, get_name_for_res_node,\
    Context
from mocdp.comp.recursive_name_labeling import (get_imp_as_recursive_dict,
                                                get_labelled_version)
from mocdp.comp.wrap import SimpleWrap
from mocdp.exceptions import DPInternalError
from mocdp.memoize_simple_imp import memoize_simple
from mocdp.ndp.named_coproduct import NamedDPCoproduct
from reprep import Report


class ValueMissing(Exception):
    pass

@contract(ndp_name='tuple')
def get_value_from_impdict(imp_dict, ndp_name):
    assert isinstance(ndp_name, tuple), ndp_name
    if not ndp_name:
        return imp_dict
    
    k = ndp_name[0]

#     isitf, is_fname = is_fun_node_name(k)
#     if isitf:
#         use = is_fname
#     else:
#         isitr, is_rname = is_res_node_name(k)
#         if isitr:
#             use = is_rname
#         else:
#             use = k
    use = k
    if not use in imp_dict:
        msg = 'get_value_from_impdict: Expected to see key %r among %s' % (use, list(imp_dict))
        raise_desc(ValueMissing, msg)

    sub = imp_dict[use]

    try:
        return get_value_from_impdict(sub, ndp_name[1:])
    except ValueMissing as e:
        msg = 'get_value_from_impdict: Cannot find value for %s.' % ndp_name.__str__()
        raise_wrapped(ValueMissing, e, msg, imp_dict=imp_dict, compact=True)

def get_ndp_recursive(ndp, ndp_name):
    assert isinstance(ndp_name, tuple), ndp_name
    if not ndp_name:
        return ndp
    k = ndp_name[0]
    if isinstance(ndp, CompositeNamedDP):
        children = ndp.get_name2ndp()
        use = k
        if not use in children:
            msg = 'get_ndp_recursive: Expected to see key %r in %s' % (use, list(children))
            raise_desc(ValueMissing, msg, key=use)
     
        child = children[use]
    elif isinstance(ndp, NamedDPCoproduct):
        i = ndp.labels.index(k)
        child = ndp.ndps[i]
    else:
        msg = 'get_ndp_recursive(%s, %s)' % (type(ndp), ndp_name)
        raise_desc(DPInternalError, msg, ndp=ndp)
    return get_ndp_recursive(child, ndp_name[1:])

class GetValues(PlottingInfo):
    def __init__(self, ndp, imp_dict, nl, nu):
        self.ndp = ndp
        self.imp_dict = imp_dict
        self.nl = nl
        self.nu = nu
        self.VALUE_FOR_MISSING = '!'

    def get_ndp(self, ndp_name):
        return get_ndp_recursive(self.ndp, ndp_name)

    def should_I_expand(self, ndp_name, alternative):
        imp = get_value_from_impdict(self.imp_dict, ndp_name)
        return alternative in imp

    @memoize_simple
    def _evaluate(self, ndp_name):
        imp = get_value_from_impdict(self.imp_dict, ndp_name)
        ndp = self.get_ndp(ndp_name)
        dp0 = ndp.get_dp()
        if self.nl is not None:
            dp, _ = get_dp_bounds(dp0, self.nl, 1)
        elif self.nu is not None:
            dp, _ = get_dp_bounds(dp0, 1, self.nu)
        else:
            dp = dp0
        I = dp.get_imp_space()
        try:
            I.belongs(imp)
        except NotBelongs as e:
            msg = 'Invalid value for implementation of %s.' % ndp_name.__str__()
            raise_wrapped(DPInternalError, e, msg, imp=imp, I=I)
        lf, ur = dp.evaluate(imp)
        return ndp, (lf, ur)

    @contract(ndp_name='tuple')
    def get_fname_label(self, ndp_name, fname):
        try:
            ndp = self.get_ndp(ndp_name)
        except DPInternalError as e:
            msg = 'get_fname_label(%s,%s) failed' % (ndp_name, fname)
            raise_wrapped(DPInternalError, e, msg, compact=True)

        if isinstance(ndp, CompositeNamedDP):
            child = get_name_for_fun_node(fname)
            return self.get_fname_label(ndp_name + (child,), fname)

        if isinstance(ndp, NamedDPCoproduct):
            imp = get_value_from_impdict(self.imp_dict, ndp_name)
            assert isinstance(imp, dict) and len(imp) == 1, imp
            which = list(imp)[0]
            return self.get_fname_label(ndp_name + (which,), fname)

        try:
            ndp, (lf, _) = self._evaluate(ndp_name)
        except ValueMissing:
            if isinstance(ndp, SimpleWrap) and isinstance(ndp.dp, (Mux, IdentityDP)):
                # Muxes and identities could be optimized away and disappear
                print('get_fname_label: Ignoring %s / %s because could be optimized away' % (ndp_name, fname))
                return self.VALUE_FOR_MISSING
            else:
                raise
                # logger.error(e)
                # return self.VALUE_FOR_MISSING
        except DPInternalError as e:
            msg = 'Could not get %r fname %r' % (ndp_name, fname)
            raise_wrapped(DPInternalError, e, msg)

        fnames = ndp.get_fnames()
        assert fname in fnames

        if len(fnames) > 1:
            i = fnames.index(fname)
            lf = lowerset_project(lf, i)

        assert isinstance(lf, LowerSet)
        if len(lf.maximals) == 1:
            one = list(lf.maximals)[0]
            return lf.P.format(one)
        
        return lf.__str__()


    @contract(ndp_name='tuple')
    def get_rname_label(self, ndp_name, rname):

        ndp = self.get_ndp(ndp_name)
        if isinstance(ndp, CompositeNamedDP):
            child = get_name_for_res_node(rname)
            return self.get_rname_label(ndp_name + (child,), rname)
        
        if isinstance(ndp, NamedDPCoproduct):
            imp = get_value_from_impdict(self.imp_dict, ndp_name)
            assert isinstance(imp, dict) and len(imp) == 1, imp
            which = list(imp)[0]
            return self.get_rname_label(ndp_name + (which,), rname)

        try:
            ndp, (_, ur) = self._evaluate(ndp_name)
        except ValueMissing:
            if isinstance(ndp, SimpleWrap) and isinstance(ndp.dp, (Mux, IdentityDP)):
                # Muxes and identities could be optimized away
                # and disappear
                print(('get_rname_label: Ignoring %s / %s because '
                      'could be optimized away') % (ndp_name, rname))
                return self.VALUE_FOR_MISSING
            else:
                raise
                # logger.error(e)
                # return self.VALUE_FOR_MISSING
        except DPInternalError as e:
            msg = 'Could not get %r rname %r' % (ndp_name, rname)
            raise_wrapped(DPInternalError, e, msg)

        rnames = ndp.get_rnames()
        assert rname in rnames

        if len(rnames) > 1:
            i = rnames.index(rname)
            ur = upperset_project(ur, i)

        assert isinstance(ur, UpperSet)
        if len(ur.minimals) == 1:
            one = list(ur.minimals)[0]
            return ur.P.format(one)
        
        return ur.__str__()


@comptest
def check_ndp_grap_imp1():
    libname = 'batteries_nodisc'
    ndpname = 'batteries'
    query = dict(missions='600 []', capacity='10 MJ')
    out = 'out/check_ndp_grap_imp1'
    plot_different_solutions(libname, ndpname, query, out)


@comptest
def check_ndp_grap_imp2():
    libname = 'batteries_v1'
    ndpname = 'batteries'
    query = dict(missions='600 []', capacity='10 MJ')
    out = 'out/check_ndp_grap_imp2'
    plot_different_solutions(libname, ndpname, query, out)
    

@comptest
def check_ndp_grap_imp3():
    libname = 'droneD_complete_templates'
    ndpname = 'test3'
    query = dict(num_missions='600 []',
                 travel_distance='10 km',
                 carry_payload='10g')
    out = 'out/check_ndp_grap_imp3'
    plot_different_solutions(libname, ndpname, query, out, upper=100)


@comptest
def check_ndp_grap_imp4():
    libname = 'droneD_complete_templates'
    ndpname = 'drone_unc3'
    query = dict(num_missions='600 []',
                 travel_distance='10 km',
                 carry_payload='10g')
    out = 'out/check_ndp_grap_imp4'
    plot_different_solutions(libname, ndpname, query, out, upper=100)


def plot_different_solutions(libname, ndpname, query, out, upper=None):
    if not os.path.exists(out):
        os.makedirs(out)
    library = get_test_library(libname)
    #library.use_cache_dir(os.path.join(out, 'cache'))
    context = Context()
    ndp = library.load_ndp(ndpname, context)

    context = library._generate_context_with_hooks()
    ndp_labelled = get_labelled_version(ndp)
    dp0 = ndp_labelled.get_dp()
    if upper is not None:
        _, dpU = get_dp_bounds(dp0, nl=1, nu=upper)
        dp = dpU
    else:
        dp = dp0

    M = dp.get_imp_space()

    with open(os.path.join(out, 'ndp.txt'), 'w') as f:
        f.write(ndp.repr_long())
    with open(os.path.join(out, 'M.txt'), 'w') as f:
        f.write(M.repr_long())
    with open(os.path.join(out, 'dp.txt'), 'w') as f:
        f.write(dp.repr_long())
    with open(os.path.join(out, 'dp0.txt'), 'w') as f:
        f.write(dp0.repr_long())

    f = convert_string_query(ndp=ndp, query=query, context=context)

    report = Report()

    res = dp.solve(f)
    print('num solutions: %s' % len(res.minimals))
    for ri, r in enumerate(res.minimals):
        ms = dp.get_implementations_f_r(f, r)

        for j, m in enumerate(ms):
            imp_dict = get_imp_as_recursive_dict(M, m)
            print imp_dict

            images_paths = library.get_images_paths()
            gv = GetValues(ndp=ndp, imp_dict=imp_dict, nu=upper, nl=1)

            gg = gvgen_from_ndp(ndp=ndp, style=STYLE_GREENREDSYM,
                                images_paths=images_paths,
                                plotting_info=gv)

            with report.subsection('%s-%s' % (ri, j)) as rr:
                gg_figure(rr, 'figure', gg, do_png=True, do_pdf=False,
                          do_svg=False, do_dot=False)


    fn = os.path.join(out, 'solutions.html')
    print('writing to %s' % fn)
    report.to_html(fn)


