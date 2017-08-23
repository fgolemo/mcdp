from comptests.registrar import comptest, run_module_tests
from mcdp_utils_xml.parsing import bs
from mcdp.logs import logger
from contracts.utils import indent
from mcdp_docs.github_file_ref.reference import parse_github_file_ref
from mcdp_docs.github_file_ref.substitute_github_refs_i import resolve_reference
from bs4.element import Tag
from mcdp.exceptions import DPSemanticError
import os

def display_files(soup, defaults):
    n = 0 
    for element in soup.find_all('display-file'):
        href = element.attrs.get('src', '')
        if href.startswith('github:'):
            display_file(element, defaults)
            n += 1
        else:
            msg = 'Unknown schema %r; I only know "github:".' % href
            raise DPSemanticError(msg)
        
    return n

def display_file(element, defaults):
    assert element.name == 'display-file'
    assert 'src' in element.attrs
    src = element.attrs['src']
    assert src.startswith('github:')
    ref = parse_github_file_ref(src)
    ref = resolve_reference(ref, defaults=defaults)
    
    lines = ref.contents.split('\n')
    a = ref.from_line if ref.from_line is not None else 0
    b = ref.to_line if ref.to_line is not None else len(lines)-1
    portion = lines[a:b+1]
    contents = "\n".join(portion)
    
    div = Tag(name='div')
    base = os.path.basename(ref.path)
    short = base +'-%d-%d' % (a,b)
    div.attrs['figure-id'] = 'code:%s' % short
    figcaption = Tag(name='figcaption')
    t=Tag(name='code')
    t.append(base)
    a = Tag(name='a')
    a.append(t)
    a.attrs['href'] = ref.url
    figcaption.append(a)
    div.append(figcaption)
    pre = Tag(name='pre')
    code = Tag(name='code')
    pre.append(code)
    code.append(contents)
    div.append(pre)
    element.replace_with(div)

    
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
     
    
    
    
    
    
        
if __name__ == '__main__':
    run_module_tests()