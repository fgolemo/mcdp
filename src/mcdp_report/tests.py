from .gg_ndp import gvgen_from_ndp
from .report import report_dp1, report_ndp1
from mocdp.unittests.generation import (for_all_dps_dyn, for_all_nameddps,
    for_all_nameddps_dyn)

@for_all_dps_dyn
def dp1_report(context, _id_dp, dp):
    r = context.comp(report_dp1, dp)
    context.add_report(r, 'dp1')


@for_all_nameddps_dyn
def ndp1_report(context, _id_dp, ndp):
    r = context.comp(report_ndp1, ndp)
    context.add_report(r, 'ndp1')


@for_all_nameddps
def graph_default(_, ndp):
    _gg = gvgen_from_ndp(ndp, style='default')


@for_all_nameddps
def graph_greenred(_, ndp):
    _gg = gvgen_from_ndp(ndp, style='greenred')


@for_all_nameddps
def graph_clean(_, ndp):
    _gg = gvgen_from_ndp(ndp, style='clean')


@for_all_nameddps
def graph_greenredsym(_, ndp):
    _gg = gvgen_from_ndp(ndp, style='greenredsym')
