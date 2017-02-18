from bs4 import BeautifulSoup
from bs4.element import NavigableString


__all__ = [
    'project_html',
]

def project_html(html):
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