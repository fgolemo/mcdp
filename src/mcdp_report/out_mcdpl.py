# -*- coding: utf-8 -*-
from mcdp_lang.parts import CDPLanguage
from mcdp_lang.utils_lists import is_a_special_list


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
#         print('type %s %s' % (type(x).__name__, d))
        orig0 = x.where.string[x.where.character:x.where.character_end]
        k0 = list(d)[0]
        v0 = d[k0]
    
        wsbefore, _, wsafter = extract_ws(orig0)
         
        out = wsbefore + str(v0) + wsafter
        yield Snippet(op=x, orig=orig0, a=x.where.character, b=x.where.character_end,
              transformed=out)

def extract_ws(s):
    """ Return initial, x, final such that initial+x+final = s """
    if not s:
        return '','',''
    assert len(s) >= 1
    i = 0
    is_ws = lambda x: x in [' ', '\n', '\t'] 
    while is_ws(s[i]) and i < len(s): 
        i += 1
    initial = s[:i]
    j = len(s) - 1
    while is_ws(s[j]) and j >= 0:
        j -= 1
    
    final = s[j+1:]
    rest = s[i:j+1]
    recombine = initial+rest+final 
    assert recombine == s, (s, initial, rest, final)
    
    return initial, rest, final 
    
def ast_to_mcdpl_inner(x):
    from mcdp_report.html import Snippet, iterate_, iterate_check_order, order_contributions
    from mcdp_report.html import iterate_notwhere
    from mcdp_lang.namedtuple_tricks import isnamedtuplewhere
    
    subcontribs = iterate3(ast_to_mcdpl_inner, x)
    subs = list(iterate_check_order(x, order_contributions(subcontribs)))

    if is_a_special_list(x):
        for _ in subs:
            yield _
        return

    cur = x.where.character
    out = ""
    for _op, _orig, a, b, transformed in subs:
#         print('chunk %s (orig=%r) gave %r r' % (type(_op).__name__,_orig, transformed))
        if a > cur:
#             print('chunk %s gave %r skipped a part: %r' % (transformed, x.where.string[cur:a]))
            out += x.where.string[cur:a]
        out += transformed
        cur = b

    if cur != x.where.character_end:
        out += x.where.string[cur:x.where.character_end]

    orig0 = x.where.string[x.where.character:x.where.character_end]
  
    yield Snippet(op=x, orig=orig0, a=x.where.character, b=x.where.character_end,
                  transformed=out)
