from comptests.registrar import comptest, run_module_tests
from mcdp.logs import logger
from mcdp_docs.github_file_ref.display_file_imp import display_files
from mcdp_docs.github_file_ref.reference import parse_github_file_ref, InvalidGithubRef
from mcdp_docs.github_file_ref.substitute_github_refs_i import substitute_github_refs
from mcdp_utils_xml.parsing import bs

from contracts.utils import indent


@comptest
def displayfile1():
    defaults = {'org': 'AndreaCensi', 
                'repo': 'mcdp',
                'branch': 'duckuments'}
     
    s = """
<display-file src="github:path=context_eval_as_constant.py,from_text=get_connections_for,to_text=return"></a> 
"""
    soup = bs(s)
    n = display_files(soup, defaults)
    assert n == 1
    
    s2 = str(soup)
    logger.debug('\n'+indent(s2, '  '))
     

@comptest
def displayfile1_line_breaks():
    defaults = {'org': 'AndreaCensi', 
                'repo': 'mcdp',
                'branch': 'duckuments'}
     
    s = """
<display-file src="github:path=context_eval_as_constant.py,
from_text=get_connections_for,
to_text=return"></a> 
"""
    soup = bs(s)
    n = display_files(soup, defaults)
    assert n == 1
    
    s2 = str(soup)
    logger.debug('\n'+indent(s2, '  '))
     
     
@comptest
def sub1():
    defaults = {'org': 'AndreaCensi', 
                'repo': 'mcdp',
                'branch': 'duckuments'}
     
    s = """
<a href="github:path=context_eval_as_constant.py"></a> 
"""
    soup = bs(s)
    n = substitute_github_refs(soup, defaults)
    assert n == 1
    
    s2 = str(soup)
    logger.debug(indent(s2, '  '))
    
    expect = '<code class="github-resource-link">context_eval_as_constant.py</code>'
    if not expect in s2:
        raise Exception(s2)
    

@comptest
def sub2():
    defaults = {'org': 'AndreaCensi', 
                'repo': 'mcdp',
                'branch': 'duckuments'}
     
    s = """
<a href="github:path=context_eval_as_constant.py,from_text=get_connections_for,to_text=return"></a> 
"""
    soup = bs(s)
    n = substitute_github_refs(soup, defaults)
    assert n == 1
    
    s2 = str(soup)
    logger.debug('\n'+indent(s2, '  '))
    
    expect=  'context_eval_as_constant.py#L7-L12'
    
    if not expect in s2:
        raise Exception('No %s in %s' % (expect, s2))
    
    

@comptest
def parse1():
    expect_failure('github')
    expect_failure('github:')
    expect_failure('github:path=')
    expect_failure('github:path=,')
    expect_failure('github:,')
    expect_failure('github:notexist=one')
    expect_failure('github:from_line=1,from_text=ciao')
    expect_failure('github:to_line=1') # to without from
        
@comptest
def parse2():
    s = 'github:path=name'
    r = parse_github_file_ref(s)
    assert r.path == 'name'
    s = 'github:org=name'
    r = parse_github_file_ref(s)
    assert r.org == 'name'        
    s = 'github:branch=name'
    r = parse_github_file_ref(s)
    assert r.branch == 'name'        
    s = 'github:from_line=3'
    r = parse_github_file_ref(s)
    assert r.from_line == 3        
    s = 'github:from_text=3'
    r = parse_github_file_ref(s)
    assert r.from_text == '3'        
    s = 'github:from_line=0,to_line=3'
    r = parse_github_file_ref(s)
    assert r.to_line == 3        
    s = 'github:from_text=1,to_text=3'
    r = parse_github_file_ref(s)
    assert r.to_text == '3'        
    
    s = 'github:from_text=ciao%20come'
    r = parse_github_file_ref(s)
    assert r.from_text == "ciao come"        
    
    s = 'github:from_text=3,to_line=1'
    r = parse_github_file_ref(s)
    s = 'github:from_line=3,to_text=1'
    r = parse_github_file_ref(s)
    s = 'github:from_text=3,to_text=1'
    r = parse_github_file_ref(s)
    s = 'github:from_line=3,to_line=1'
    r = parse_github_file_ref(s)
    s = 'github:from_text=3,\nto_text=1'
    r = parse_github_file_ref(s)
    s = 'github:from_text=3, \n to_text=1'
    r = parse_github_file_ref(s)
    

def expect_failure(s):
    try:
        parse_github_file_ref(s)
    except InvalidGithubRef:
        pass
    else:
        raise Exception('expected failure for %r' % s)

    
    
        
if __name__ == '__main__':
    run_module_tests()