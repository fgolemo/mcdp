from bs4.element import Tag
from mcdp_web.renderdoc.highlight import add_class
from mcdp_utils_xml import to_html_stripping_fragment, bs

def other_abbrevs(s):
    """
        v, val, value   --> mcdp-value
           pos, poset   --> mcdp-poset
           
        <val>x</val> -> <mcdp-value></mcdp-value>
        <pos>x</pos> -> <mcdp-poset></mcdp-poset>
        
        <s> (strikeout!) -> <span> 
        
        <p>TODO:...</p> -> <div class="todo"><p><span>TODO:</span></p>
    """
    soup = bs(s)
    
    translate = {
        'v': 'mcdp-value',
        'val': 'mcdp-value',
        'value': 'mcdp-value',
        
        'pos': 'mcdp-poset',
        'poset': 'mcdp-poset',
        's': 'span',
    }
    
    for k, v in translate.items():
        for e in soup.select(k):
            e.name = v

    # fix todo
    for p in list(soup.select('p')):
        s = " ".join(p.strings) # note: strings
        
        if s is not None:
            TODO = 'TODO:'
            if s.startswith(TODO):
                without = s[len(TODO):]
                p.string = without.strip()
                div = Tag(name='div')
                add_class(div, 'todo-wrap')
                add_class(p, 'todo')
                parent = p.parent
                i = parent.index(p)
                p.extract()
                div.append(p)
                parent.insert(i, div)

    res = to_html_stripping_fragment(soup) 
    return res