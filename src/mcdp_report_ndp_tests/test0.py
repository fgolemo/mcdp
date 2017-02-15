# -*- coding: utf-8 -*-
from comptests.registrar import comptest_fails
from mcdp import logger
from mcdp_lang.syntax import Syntax
from mcdp_lang_tests.syntax_spaces import assert_equal_string
from mcdp_report.gg_ndp import gvgen_from_ndp
from mcdp_report.html import ast_to_html
from mcdp_report.report import report_dp1, report_ndp1
from mcdp_tests.generation import (for_all_dps_dyn, for_all_nameddps,
                                   for_all_nameddps_dyn, for_all_source_mcdp)
from mcdp_utils_xml import project_html


@for_all_source_mcdp
def check_syntax(filename, source, parse_expr=Syntax.ndpt_dp_rvalue):  # @UnusedVariable
    
    # skip generated files (hack)
    if filename and 'drone_unc2_' in filename:
        return
    
    # print filename
    if filename is not None:
        source = open(filename).read()
    try:
        html = ast_to_html(source,
                            parse_expr,
                           ignore_line=lambda _lineno: False,
                           add_line_gutter=False, encapsulate_in_precode=True, 
                           )
#         print html.__repr__()
        source2 = project_html(html)
#         print source
#         print source2
        # print indent(html, 'html |')
        assert_equal_string(s2_expected=source, s2=source2)
    except:
        logger.error('This happened to %r' %  filename)
        
        raise
    
if False:
    # these are all antiquate
    @for_all_dps_dyn
    def dp1_report(context, id_dp, dp):
        r = context.comp(report_dp1, dp)
        context.add_report(r, 'dp1', id_dp=id_dp)
    
    
    @for_all_nameddps_dyn
    def ndp1_report(context, id_dp, ndp):
        r = context.comp(report_ndp1, ndp)
        context.add_report(r, 'ndp1', id_dp=id_dp)
    
    
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

# 
# @comptest_fails
# def parcheck_space():
#     sources = [
#         "(J × A) × (m × s × Nat)",
#         "J x A",
#         "(J x A)",
#     ]
#     filename = None
#     parse_expr = Syntax.space_prec
#     # print parse_expr
#     for source in sources:
#         print('source = %r' % source)
#         check_syntax(filename, source, parse_expr=parse_expr)

@comptest_fails 
def parcheck_fvalue():
    sources = [
        "(1 + 1)",
        "(1 + 1) ",
        " (1 + 1)",
        " (1 + 1) ",
    ]
    filename = None
    parse_expr = Syntax.fvalue
    for source in sources:
        check_syntax(filename, source, parse_expr=parse_expr)
    
quickcheck = parcheck_fvalue
    
if __name__=='__main__':
    quickcheck()