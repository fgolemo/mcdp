from bs4 import BeautifulSoup

from contracts.utils import raise_desc


# def bs(fragment):
#     return BeautifulSoup(fragment, 'html.parser', from_encoding='utf-8')
def bs(fragment):
    """ Returns the contents wrapped in an element called "fragment".
        Expects fragment as a str in utf-8 """
    s = '<fragment>%s</fragment>' % fragment
    parsed = BeautifulSoup(s, 'lxml', from_encoding='utf-8')
    res = parsed.html.body.fragment
    assert res.name == 'fragment'
    return res

    

def to_html_stripping_fragment(soup):
    """ Returns a string encoded in UTF-8 """
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
        
## Use these for entire documents

def bs_entire_document(s):
    parsed = BeautifulSoup(s, 'lxml', from_encoding='utf-8')
    assert parsed.find('body') is not None
    return parsed

def to_html_entire_document(soup):
    return str(soup)