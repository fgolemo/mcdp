from bs4 import BeautifulSoup

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
    assert not '<html>' in s, s
    s = s.replace('<fragment>','')
    s = s.replace('</fragment>','')
    return s