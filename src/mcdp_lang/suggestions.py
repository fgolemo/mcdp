# -*- coding: utf-8 -*-

import re

from mcdp_lang.parts import CDPLanguage
from mcdp_lang.refinement import namedtuple_visitor_ext
from mocdp.exceptions import DPInternalError

__all__ = ['get_suggestions', 'apply_suggestions']

CDP = CDPLanguage

"""

    x = parse_wrap(Syntax.ndpt_dp_rvalue, s)[0]
    xr = parse_ndp_refine(x, Context())
    suggestions = get_suggestions(xr)     
    s2 = apply_suggestions(s, suggestions)


"""

def correct(x):
    x_string = x.where.string[x.where.character:x.where.character_end]
    def match_in_x_string(r):
        m = re.search(r, x_string)
        return x_string[m.start():m.end()]
    
    if isinstance(x, CDP.leq):
        if x.glyph != '≤':
            return x.glyph, '≤'
    
    if isinstance(x, CDP.geq):
        if x.glyph != '≥': 
            return x.glyph, '≥'
    
    if isinstance(x, CDP.NewFunction) and x.keyword is None:
        name = x.name.value
        return name, 'provided %s' % name
    
    if isinstance(x, CDP.NewResource) and x.keyword is None:
        name = x.name.value
        return name, 'required %s' % name
    
    if isinstance(x, CDP.Resource) and isinstance(x.keyword, CDP.DotPrep):
        dp, s = x.dp.value, x.s.value
        r = '%s.*\..*%s' % (dp, s)
        old = match_in_x_string(r)
        new = '%s required by %s' % (s, dp)
        return old, new
    
    if isinstance(x, CDP.Function) and isinstance(x.keyword, CDP.DotPrep):
        dp, s = x.dp.value, x.s.value
        r = '%s.*\..*%s' % (dp, s)
        old = match_in_x_string(r)
        new = '%s provided by %s' % (s, dp)
        return old, new

    return None

def get_suggestions(xr):
    """ Returns a sequence of (where, replacement_string) """
    subs = [] # (where, sub)
    def find_corrections(x, parents):  # @UnusedVariable
        has = correct(x)
        if has is None:
            pass
        else:
            a, b = has
            s = x.where.string[x.where.character:x.where.character_end]
            if not a in s:
                msg = 'Could not find piece %r in %r.' % (a, s)
                raise DPInternalError(msg)
            ws_before_a = s[:s.index(a)]
            sub = ws_before_a + b
            subs.append((x.where, sub))
        return x
            
    _ = namedtuple_visitor_ext(xr, find_corrections)
    return subs

def apply_suggestions(s, subs):
    """ Returns a new string applying the suggestions above. """
    chars = list(range(len(s)))
    id2char = {}
    for i, c in enumerate(s):
        id2char[i] = c
        
    for where, replacement in subs:
        assert where.string == s, (where.string, s)
        seq = list(range(where.character, where.character_end))
        i = chars.index(seq[0])
        for _ in seq:
            chars.remove(_)
            
        for j, c in enumerate(replacement):
            cid = len(id2char)
            id2char[cid] = c 
            chars.insert(i + j, cid)
    
    result = ''.join( id2char[_] for _ in chars)
    return result