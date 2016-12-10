# -*- coding: utf-8 -*-

import re

from mcdp_lang.parts import CDPLanguage
from mcdp_lang.refinement import namedtuple_visitor_ext
from mocdp.exceptions import DPInternalError
from mcdp_lang.namedtuple_tricks import recursive_print


__all__ = ['get_suggestions', 'apply_suggestions']

CDP = CDPLanguage

"""

    x = parse_wrap(Syntax.ndpt_dp_rvalue, s)[0]
    xr = parse_ndp_refine(x, Context())
    suggestions = get_suggestions(xr)     
    s2 = apply_suggestions(s, suggestions)


"""

def correct(x, parents):
    x_string = x.where.string[x.where.character:x.where.character_end]
    def match_in_x_string(r):
        m = re.search(r, x_string)
        return x_string[m.start():m.end()]
    
    # each of this has one element .glyph
    glyphs = {
        CDP.leq: '≤',
        CDP.geq: '≥',
        CDP.OpenBraceKeyword: '⟨',
        CDP.CloseBraceKeyword: '⟩',
        CDP.times: '·',
        CDP.MAPSFROM: '⟻',
        CDP.MAPSTO: '⟼',
        CDP.LEFTRIGHTARROW: '⟷',
        CDP.product: '×',
    }
    
    for klass, preferred in glyphs.items():
        if isinstance(x, klass):
            if x.glyph != preferred:
                return x.glyph, preferred
       
    symbols = {
        CDP.Nat: 'ℕ',
        CDP.Int: 'ℤ',
        CDP.Rcomp: 'ℝ',
    }     
    
    for klass, preferred in symbols.items():
        if isinstance(x, klass):
            if x.symbol != preferred:
                return x.symbol, preferred
        
    keywords = {
        CDP.TopKeyword: '⊤',
        CDP.BottomKeyword: '⊥',
        CDP.FinitePosetKeyword: 'poset',
    }
    
    for klass, preferred in keywords.items():
        if isinstance(x, klass):
            if x.keyword != preferred:
                return x.keyword, preferred

    
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
    
    if isinstance(x, CDP.RcompUnit):
        replacements = {
            '1': '¹',
            '2':'²' ,
            '3':'³',
            '4':'⁴',
            '5':'⁵',
            '6':'⁶',
            '7':'⁷',
            '8':'⁸',
            '9':'⁹',
        }
        for n, replacement in replacements.items():
            w = '^' + n
            if w in x_string:
                s2 = x_string.replace(w, replacement)
                return x_string, s2
            
            w = '^ ' + n
            if w in x_string:
                s2 = x_string.replace(w, replacement)
                return x_string, s2

    if isinstance(x, CDP.PowerShort):
#         print isinstance(parents[-1][0], CDP.PowerShort)
#         if isinstance(parents[-1][0], CDP.PowerShort):
#             print ('sub ' + x_string)
        replacements = {
            '1':'¹',
            '2':'²' ,
            '3':'³',
            '4':'⁴',
            '5':'⁵',
            '6':'⁶',
            '7':'⁷',
            '8':'⁸',
            '9':'⁹',
        }
        for n, replacement in replacements.items():
            for i in reversed(range(3)):
                for j in reversed(range(3)):
                    w = ' '*i + '^' + ' '*j + n
                    if w in x_string:
                        return w, replacement
                    
    return None

def get_suggestions(xr):
    """ Returns a sequence of (where, replacement_string) """
    subs = [] # (where, sub)
    def find_corrections(x, parents):  
        has = correct(x, parents)
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
    subs = remove_redundant_suggestions(subs)
    return subs

def remove_redundant_suggestions(subs):
    """ Removes the suggestions that conflict with others. """
    res = []
    characters_affected = set()
    for s in subs:
        w, _ = s
        chars = range(w.character, w.character_end)
        
        if any(_ in characters_affected for _ in chars):
            #print('skipping %r - %s because of conflict' % (w, r))
            pass
        else:
            res.append(s)
        characters_affected.update(chars)
    return res

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