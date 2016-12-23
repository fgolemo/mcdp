from mcdp_web.renderdoc.xmlutils import to_html_stripping_fragment, bs

def other_abbrevs(s):
    """
    
        <val>x</val> -> <mcdp-value></mcdp-value>
        <pos>x</pos> -> <mcdp-poset></mcdp-poset>
        
    """
    soup = bs(s)
    
    translate = {
        'val': 'mcdp-value',
        'pose': 'mcdp-poset',
    }
    
    for k, v in translate.items():
        for e in soup.select(k):
            e.name = v

    res = to_html_stripping_fragment(soup) 
    return res