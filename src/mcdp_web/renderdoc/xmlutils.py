from bs4 import BeautifulSoup
from contracts.utils import raise_desc, indent, check_isinstance
from bs4.element import Tag
from contracts import contract

# def bs(fragment):
#     return BeautifulSoup(fragment, 'html.parser', from_encoding='utf-8')
def bs(fragment):
    """ Returns the contents wrapped in an element called "fragment" """
    s = '<fragment>%s</fragment>' % fragment
    parsed = BeautifulSoup(s, 'lxml', from_encoding='utf-8')
    res = parsed.html.body.fragment
    assert res.name == 'fragment'
    return res

def to_html_stripping_fragment(soup):
    assert soup.name == 'fragment'
    s = str(soup)
    check_html_fragment(s)
    s = s.replace('<fragment>','')
    s = s.replace('</fragment>','')
    return s

def to_html_stripping_fragment_document(soup):
    """ Assumes it is <fragment><html>...</html></fragment> """
    assert soup.html is not None, str(soup)
    s = str(soup)
    s = s.replace('<fragment>','')
    s = s.replace('</fragment>','')
    return s
    

def check_html_fragment(m, msg=None):
    if '<html>' in m or 'DOCTYPE' in m:
        if msg is None:
            msg2 = ""
        else:
            msg2 = msg + ' '
        msg2 += 'This appears to be a complete document instead of a fragment.'
        raise_desc(ValueError, msg2, m=m)
        
@contract(tag=Tag, returns=str)
def describe_tag(tag):
    check_isinstance(tag, Tag)
    def c(tag):
        x = unicode(tag).encode('utf-8')
        return x 
    
    s = "This is the tag:"
    s += '\n\n'
    s += indent(c(tag), 'tag |')
    s +='\n\n' + 'This is the tag in context:' + '\n\n'
    
    sc = ""
    if tag.previousSibling is not None:
        sc += c(tag.previousSibling)
    else:
        sc += '<!-- no prev sibling -->'
    sc += c(tag)
    if tag.nextSibling is not None:
        sc += c(tag.next)
    else:
        sc += '<!-- no next sibling -->' 
        
    s += indent(sc, 'tag in context |')
    return s
    
    
    
    