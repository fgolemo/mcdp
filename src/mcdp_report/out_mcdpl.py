# -*- coding: utf-8 -*-
from mcdp_lang.parts import CDPLanguage
from mcdp_lang.utils_lists import is_a_special_list
from mcdp.exceptions import mcdp_dev_warning


__all__ = ['ast_to_mcdpl']

def ast_to_mcdpl(x):
    blocks = list(ast_to_mcdpl_inner(x))
    return blocks[0].transformed
    
CDP = CDPLanguage 
    
def iterate3(transform, x):
    from mcdp_report.html import iterate_notwhere
    from mcdp_lang.namedtuple_tricks import isnamedtuplewhere
    from mcdp_report.html import Snippet

    nsubs = 0
    for  _, op in iterate_notwhere(x):
        if isnamedtuplewhere(op):
            for m in transform(op):
                nsubs += 1
                yield m

    d = x._asdict()
    if len(d) == 1 + 1 and nsubs==0:
        orig0 = x.where.string[x.where.character:x.where.character_end]
        k0 = list(d)[0]
        v0 = d[k0]
    
        wsbefore, _, wsafter = extract_ws(orig0)
         
        out = wsbefore + str(v0) + wsafter
        yield Snippet(op=x, orig=orig0, a=x.where.character, b=x.where.character_end,
              transformed=out)

mcdp_dev_warning('TODO: extract_ws() used by mcdp_lnag, move in utils')
def extract_ws(s, ws_chars = [' ', '\n', '\t']):
    """ Return initial, x, final such that initial + x + final = s """
    if not s:
        return '', '', ''
    
    assert len(s) >= 1
    
    i = 0
    is_ws = lambda x: x in ws_chars 
    
    # i is the first character that is not a whitespace
    while i < len(s) and is_ws(s[i]): 
        i += 1
        
    # now we know the initial string
    initial = s[:i]
    
    # rest of the string (middle + final)
    rest = s[i:]
    
    len_final = 0
    while len_final < len(rest) and is_ws(rest[len(rest)-len_final-1]):
        len_final += 1
    
    final = s[len(s)-len_final:]
    middle = s[i:len(s)-len_final]
    recombine = initial + middle + final 
    
    assert recombine == s, (s, initial, middle, final)
    
    return initial, middle, final 
    
def ast_to_mcdpl_inner(x):
    from mcdp_report.html import Snippet, iterate_check_order, order_contributions
    
    subcontribs = iterate3(ast_to_mcdpl_inner, x)
    subs = list(iterate_check_order(x, order_contributions(subcontribs)))

    if is_a_special_list(x):
        for _ in subs:
            yield _
        return

    cur = x.where.character
    out = ""
    for _op, _orig, a, b, transformed in subs:
        if a > cur:
            out += x.where.string[cur:a]
        out += transformed
        cur = b

    if cur != x.where.character_end:
        out += x.where.string[cur:x.where.character_end]

    orig0 = x.where.string[x.where.character:x.where.character_end]
  
    yield Snippet(op=x, orig=orig0, a=x.where.character, b=x.where.character_end,
                  transformed=out)
