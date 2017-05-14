from comptests.registrar import comptest, run_module_tests
from mcdp_docs.elements_abbrevs import substitute_special_paragraphs
from mcdp_utils_xml.parsing import bs, to_html_stripping_fragment

from nose.tools import assert_equal


@comptest
def elements_abbrevs_test1():
    s = "<p>TODO: paragraph</p>"
    e = """<div class="todo-wrap"><p class="todo">paragraph</p></div>"""
    soup = bs(s.strip())
    
    substitute_special_paragraphs(soup)
    
    o = to_html_stripping_fragment(soup)
    #print o
    assert_equal(o, e)
    

@comptest
def elements_abbrevs_test2():
    s = "<p>TODO: paragraph <strong>Strong</strong></p>"
    e = """<div class="todo-wrap"><p class="todo">paragraph <strong>Strong</strong></p></div>"""
    soup = bs(s.strip())
    
    substitute_special_paragraphs(soup)
    
    o = to_html_stripping_fragment(soup)
    #print o
    assert_equal(o, e)
    
    
if __name__ == '__main__':
    run_module_tests()