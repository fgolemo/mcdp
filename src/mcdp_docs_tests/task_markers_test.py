from comptests.registrar import comptest, run_module_tests
from mcdp_docs.task_markers import substitute_task_markers
from mcdp_utils_xml.parsing import bs, to_html_stripping_fragment

from nose.tools import assert_equal


@comptest
def task_markers_test1():
    s = "<p>We should do this (TODO)</p>"
    e = """<p class="status-todo">We should do this </p>"""
    soup = bs(s.strip())
    
    substitute_task_markers(soup)
    
    o = to_html_stripping_fragment(soup)
    #print o
    assert_equal(o, e)
    
    
if __name__ == '__main__':
    run_module_tests()