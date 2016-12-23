'''

This:

    <col2>
    <a>
    <b>
    <c>
    ...
    </col2>

becomes
    <table class='col2'>
        <tr><td> 
            <a>
        </td><td>
            <b>
        <tr></tr>
    </table>

'''
import math
from mcdp_web.renderdoc.xmlutils import bs, to_html_stripping_fragment,\
    describe_tag
from bs4 import BeautifulSoup
from bs4.element import NavigableString, Tag, Comment
from contracts.utils import raise_desc
from mocdp import logger

__all__ = [
    'col_macros_prepare_before_markdown',
    'col_macros',
]

ns = [1,2,3,4,5]
def col_macros_prepare_before_markdown(s):
    """ MD doesn't like <col2> as top-level element """
    for n in ns:
        s = s.replace('<col%d'%n ,'<div class="make-col%d" '%n)
        s = s.replace('</col%d>'%n ,'</div>')
    return s

def col_macros(html):
    for n in ns:
        html = col_macro(html, n)
    return html

def col_macro(html, n):
    assert n in ns
    soup = bs(html)
    selector = 'div.make-col%d' % n
    num = 0
    for e in soup.select(selector):
        col_macro_(e, n)
        num += 1
    if num == 0:
        logger.debug('No elements matching %r found.' % selector)
    else:
        logger.debug('Found %d elements matching %r.' % (num, selector))
    res = to_html_stripping_fragment(soup) 
    return res

def col_macro_(e, ncols):
    """
        Bug: For some reasone bd4 removes the whitespace I use for indentation.
        
    
    """
    assert e.name == 'div' 
    assert 'make-col%d' % ncols in e['class']
    
    children = list(e.children) 
    # remove strings from this
    is_string = lambda x: isinstance(x, NavigableString)
    strings = [_ for _ in children if is_string(_)]
    children = [_ for _ in children if not is_string(_)]
    
    if len(children) < ncols:
        msg = 'Cannot create table with %r cols with only %d children' % (ncols, len(children))
        raise_desc(ValueError, msg, tag=describe_tag(e))
    
    for c in children:
        c.extract()
        
    for s in strings:
        ss = str(s)
        empty = not ss.strip()
        if not empty:
            msg = 'Found nonempty string %r between children.' % ss 
            raise_desc(ValueError, msg, tag=describe_tag())
        # remove it
        s.extract()
        
    nchildren = len(children)
    nrows = int(math.ceil(nchildren / float(ncols)))
    
    e.name = 'div'
    from mcdp_web.renderdoc.highlight import add_class
    add_class(e, 'col%d-wrap'%ncols)
    add_class(e, 'colN-wrap')
    table = Tag(name='table')
    add_class(table, 'col%d'%ncols)
    add_class(table, 'colN')
    add_class(table, 'col%d-created'%ncols)
    NL = '\n'
    # S = '-' * 4
    # XXX: change to above to see the problem with indentation
    S = ' ' * 4
    for row in range(nrows):
        tr = Tag(name='tr')
        tr.append(NavigableString(NL))
        for col in range(ncols):
            td = Tag(name='td')
            i = col + row * ncols
            if i < len(children):
                child = children[i]
                td.append(child)
            else:
                td.append(Comment('empty row %d col %d' % (row, col)))
            tr.append(NavigableString(S+S+S))
            tr.append(td)
            tr.append(NavigableString(NL))
        tr.append(S+S)
        table.append(NavigableString(NL))
        table.append(NavigableString(S+S))
        table.append(tr)   
        table.append(NavigableString(NL+S))
    e.append(NavigableString(NL + S))  
    e.append(table)
    e.append(NavigableString(NL))
    # XXX
    i = e.parent.index(e)
    e.parent.insert(i, e) 
    
    