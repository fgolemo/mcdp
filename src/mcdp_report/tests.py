from .gg_ndp import gvgen_from_ndp
from .report import report_dp1, report_ndp1
from mcdp_report.html import ast_to_html
from mcdp_tests.generation import (for_all_dps_dyn, for_all_nameddps,
    for_all_nameddps_dyn, for_all_source_mcdp)

@for_all_source_mcdp
def check_syntax(filename, source):
    # print filename
    html = ast_to_html(source,
                       complete_document=False, extra_css="",
                       ignore_line=lambda _lineno: False,
                       add_line_gutter=True, encapsulate_in_precode=True, add_css=True)
    # print html

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
