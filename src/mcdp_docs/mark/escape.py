from mcdp_utils_xml.parsing import to_html_stripping_fragment, bs
import bs4

def escape_ticks_before_markdown(html):
    """ Escapes backticks and quotes in code 
    
        Also removes comments <!--- -->
    """
    soup = bs(html)
    for code in soup.select('code, pre, mcdp-poset, mcdp-value, mcdp-fvalue, mcdp-rvalue, render'):
        if not code.string:
            continue
        #unicode
        s = code.string
        if '`' in code.string:
            s = s.replace('`', '&#96;')
#             print('replacing %r -> %r' %(code.string, s))
            
            
        if '"' in code.string:
            s = s.replace('"', '&quot;')
#             print('replacing %r -> %r' %(code.string, s))
            
        code.string = s
    
    comments=soup.find_all(string=lambda text:isinstance(text, bs4.Comment))
    for c in comments:
#         print('stripping comment %s' % str(c))
        c.extract()
    
    res = to_html_stripping_fragment(soup)
     
    return res