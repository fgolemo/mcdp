from contracts.utils import check_isinstance
from contracts import contract
from bs4.element import Tag

def add_style(tag, after=True, **kwargs):
    """    
        add_style(tag, width="2in")
    """
    def quote(x):
        return x
    s1 = '; '.join('%s: %s' % (k, quote(v)) for k,v in kwargs.items())
    s0 = tag.attrs.get('style', None)
    
    if s0 is None:
        s = s1
    else:
        s0 = s0.rstrip();
        if after:
            if not s0.endswith(';'):
                s0 += ';'
            s = s0 + s1
        else:
            if not s1.endswith(';'):
                s1 += ';' 
            s = s1 + s0
    tag['style'] = s
    
@contract(e=Tag, c='str|list(str)')
def add_class(e, c):
    check_isinstance(e, Tag)
    if isinstance(c, str):    
        cc = [_ for _ in c.split(' ') if _]
    elif isinstance(c, list):
        for _ in c:
            check_isinstance(_, str)
        cc = c
    else:
        raise ValueError(c)
    cur = e.attrs.get('class', [])
    if isinstance(cur, str):
        cur = [_ for _ in cur.split() if _] # remove None
    
    check_isinstance(cur, list)
    cur = cur + cc
    e.attrs['class'] = cur 
    # check not None
    for classname in e.attrs['class']:
        assert classname is not None
    