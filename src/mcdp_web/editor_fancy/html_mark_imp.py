from bs4 import BeautifulSoup
from contracts import contract
from contracts.utils import check_isinstance, raise_desc

from mcdp.exceptions import DPInternalError
from mcdp_report.html import ATTR_WHERE_CHAR, ATTR_WHERE_CHAR_END


@contract(html=bytes, returns=bytes)
def html_mark(html, where, add_class, tooltip=None):
    """ Takes a utf-8 encoded string and returns another html string. 
    
        The tooltip functionality is disabled for now.
    """
    check_isinstance(html, bytes)
    
    html = '<www><pre>' + html + '</pre></www>'
    soup = BeautifulSoup(html, 'lxml', from_encoding='utf-8')

    elements = soup.find_all("span")
    
    found = [] 
    
    for e in elements:
        if e.has_attr(ATTR_WHERE_CHAR):
            character = int(e[ATTR_WHERE_CHAR])
            character_end = int(e[ATTR_WHERE_CHAR_END])
            #print (where.character, character, character_end, where.character_end)
            # inside = where.character <= character <= character_end <= where.character_end
            inside = character <= where.character <= where.character_end <= character_end
            if inside:
                found.append(e)
                
    if not found:
        msg = 'Cannot find any html element for this location:\n\n%s' % where
        msg += '\nwhere start: %s end: %s' % (where.character, where.character_end)
        msg += '\nwhere.string = %r' % where.string
        msg += '\n' + html.__repr__()
        raise_desc(DPInternalError, msg)
        
    # find the smallest one
    def e_size(e):
        character = int(e[ATTR_WHERE_CHAR])
        character_end = int(e[ATTR_WHERE_CHAR_END])
        l = character_end - character
        return l
    
    ordered = sorted(found, key=e_size)
        
    e2 = ordered[0]    
    e2['class'] = e2.get('class', []) + [add_class]
    
    if tooltip is not None:
        script = 'show_tooltip(this, %r);' % tooltip
        tooltip_u =  unicode(tooltip, 'utf-8') 
        e2['onmouseover'] = script
        e2['title'] = tooltip_u 
        
    pre = soup.body.www
    s = str(pre)
    s = s.replace('<www><pre>', '')
    s = s.replace('</pre></www>', '')
    assert isinstance(s, str)
    return s
    
def html_mark_syntax_error(string, e):
    where = e.where
    character = where.character
    first = string[:character]
    rest = string[character:]
    s = "" + first + '<span style="color:red">'+rest + '</span>'
    return s 
