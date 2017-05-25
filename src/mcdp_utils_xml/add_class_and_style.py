from contracts.utils import check_isinstance

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
    
def add_class(e, c):
    if isinstance(c, str):    
        cc = c.split(' ')
    elif isinstance(c, list):
        for _ in c:
            check_isinstance(_, str)
        cc = c
    else:
        raise ValueError(c)
    cur = e.get('class', [])
    if isinstance(cur, str):
        cur = cur.split()
    cur = cur + cc
    e['class'] = cur 
    