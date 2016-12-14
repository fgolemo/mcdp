# -*- coding: utf-8 -*-
from mcdp_lang.syntax import Syntax
from mcdp_report.gg_ndp import gvgen_from_ndp
from mcdp_report.html import ast_to_html
from mcdp_report.report import report_dp1, report_ndp1
from mcdp_tests.generation import (for_all_dps_dyn, for_all_nameddps,
    for_all_nameddps_dyn, for_all_source_mcdp)
from mocdp import logger
from nose.tools import assert_equal
from bs4.element import NavigableString

def project_html(html):
    from bs4 import BeautifulSoup
    doc = BeautifulSoup(html, 'lxml', from_encoding='utf-8')
    res = gettext(doc, 0)
    return res

def gettext(element, n):
    # print('%d %s element %r' % (n, '  ' * n, element.string))
    
    if isinstance(element, NavigableString):
        string = element.string
        if string is None:
            return ''
        else:
            return string.encode('utf-8')
    else:
        out = ''
        for child in element.children:
            out += gettext(child, n + 1)
     
        return out
    

@for_all_source_mcdp
def check_syntax(filename, source):  # @UnusedVariable
    
    # skip generated files (hack)
    if 'drone_unc2_' in filename:
        return
    
    # print filename
    source = open(filename).read()
    try:
        html = ast_to_html(source,
                            parse_expr=Syntax.ndpt_dp_rvalue,
                           ignore_line=lambda _lineno: False,
                           add_line_gutter=False, encapsulate_in_precode=True, 
                           )
#         print html.__repr__()
        source2 = project_html(html)
#         print source
#         print source2
        assert_equal(source, source2)
    except:
        logger.error('This happened to %r' %  filename)
        
        raise

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
