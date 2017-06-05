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
import re

from bs4.element import NavigableString, Tag, Comment

from contracts.utils import raise_desc


from mcdp_utils_xml import describe_tag, add_class


__all__ = [
    'col_macros_prepare_before_markdown',
    'col_macros',
]

ns = [1,2,3,4,5,6,7,8,9,10  ]
def col_macros_prepare_before_markdown(s):
    """ MD doesn't like <col2> as top-level element """
#     for n in ns:
#         s = s.replace('</col%d>'%n ,'</div>')
    s = re.sub(r'<(col\d)(.*?)>', r'<div make-\1=""\2>', s, flags = re.M | re.DOTALL)
    s = re.sub(r'<\/(col\d)>', '</div>', s, flags = re.M | re.DOTALL)


    s = re.sub(r'<center(.*?)>', r'<div center=""\1>', s, flags = re.M | re.DOTALL)
    s = re.sub(r'<\/center>', '</div>', s, flags = re.M | re.DOTALL)

    return s

def col_macros(soup):
    for n in ns:
        col_macro(soup, n)

def col_macro(soup, n):
    assert n in ns
    selector = 'div[make-col%d]' % n
    num = 0
    for e in soup.select(selector):
        col_macro_(e, n)
        num += 1
    if num == 0:
        pass
        #logger.debug('No elements matching %r found.' % selector)
    else:
        pass
        #logger.debug('Found %d elements matching %r.' % (num, selector))

def col_macro_(e, ncols):
    """
        Bug: For some reasone bd4 removes the whitespace I use for indentation.
        
    
    """
    assert e.name == 'div' 
    assert e.has_attr('make-col%d' % ncols)
    
#     print describe_tag(e)
    children = list(e.children) 
    # remove strings from this
    is_string = lambda x: isinstance(x, NavigableString)
    strings = [_ for _ in children if is_string(_)]
    children = [_ for _ in children if not is_string(_)]
    
    if len(children) < ncols:
        msg = ('Cannot create table with %r cols with only %d children' % 
               (ncols, len(children)))
        raise_desc(ValueError, msg, tag=describe_tag(e))
    
    for c in children:
        c.extract()
        
    for s in strings:
        ss = str(s)
        empty = not ss.strip()
        if not empty:
            msg = 'Found nonempty string %r between children.' % ss 
            raise_desc(ValueError, msg, tag=describe_tag(e))
        # remove it
        s.extract()
        
    nchildren = len(children)
    nrows = int(math.ceil(nchildren / float(ncols)))
    
    parent = e.parent
    original_position = parent.index(e)
    e.extract()
    table = e
    e.name = 'table'
    add_class(table, 'col%d' % ncols)
    add_class(table, 'colN') 
    
    wrapper = Tag(name='div')
    add_class(wrapper, 'col%d-wrap' % ncols)
    add_class(wrapper, 'colN-wrap')
    
    NL = '\n'
    # S = '-' * 4
    # XXX: change to above to see the problem with indentation
    S = ' ' * 4
    tbody = Tag(name='tbody')
    for row in range(nrows):
        tbody.append(NavigableString(NL))
        tbody.append(NavigableString(S+S))
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
        if row == 0 and ('labels-row1' in e.attrs.get('class', '')):
            thead = Tag(name='thead')
            thead.append(tr)
            table.append(thead) # add in table, not tbody
        else:
            tbody.append(tr)   # add in tbody
        tbody.append(NavigableString(NL+S))
    table.append(tbody)
    
    wrapper.append(NavigableString(NL + S))  
    wrapper.append(table)
    wrapper.append(NavigableString(NL))
    
    parent.insert(original_position, wrapper) 
    
    