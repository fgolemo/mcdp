# -*- coding: utf-8 -*-


"""
    Example usage:

        x = parse_wrap(Syntax.ndpt_dp_rvalue, s)[0]
        xr = parse_ndp_refine(x, Context())
        suggestions = get_suggestions(xr)     
        s2 = apply_suggestions(s, suggestions)


"""

import re

from mcdp_lang.parts import CDPLanguage
from mcdp_lang.refinement import namedtuple_visitor_ext
from mocdp.exceptions import DPInternalError
from mcdp_lang.dealing_with_special_letters import subscripts, greek_letters
from contracts.utils import check_isinstance
from contracts.interface import Where
from contracts import contract


__all__ = [
    'get_suggestions', 
    'apply_suggestions',
]

CDP = CDPLanguage

def correct(x, parents):  # @UnusedVariable
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
            w = '^' + n
            if w in x_string:
                s2 = x_string.replace(w, replacement)
                return x_string, s2
            
            w = '^ ' + n
            if w in x_string:
                s2 = x_string.replace(w, replacement)
                return x_string, s2

    if isinstance(x, CDP.PowerShort):
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
                    w = ' ' * i + '^' + ' ' * j + n
                    if w in x_string:
                        return w, replacement
                    
    if isinstance(x, (CDP.VName, CDP.RName, CDP.FName, CDP.CName)):
        suggestion = get_suggestion_identifier(x_string)
        if suggestion is not None:
            return suggestion
        
    return None

@contract(s=bytes, returns='tuple')
def get_suggestion_identifier(s):
    """ Returns a pair of what, replacement, or None if no suggestions available""" 
    check_isinstance(s, bytes)
    for num, subscript in subscripts.items():
        s0 = '_%d' % num
        if s.endswith(s0):
            return s0, subscript.encode('utf8')
    for name, letter in greek_letters.items():
        if name.encode('utf8') in s:
            # yes: 'alpha_0'
            # yes: 'alpha0'
            # no: 'alphabet'
            i = s.index(name)
            letter_before = None if i == 0 else s[i-1:i]
            a = i + len(name)
            letter_after = None if a == len(s) - 1 else s[a:a+1]
            
            dividers = ['_','0','1','2','3','4','5','6','7','8','9']
            ok1 = letter_before is None or letter_before in dividers
            ok2 = letter_after is None or letter_after in dividers
            if ok1 and ok2:
                return name.encode('utf8'), letter.encode('utf8')
    return None
    
def get_suggestions(xr):
    """ Returns a sequence of (where, replacement_string) """
    subs = [] # (where, sub)
    def find_corrections(x, parents):
        # expect two pairs of strings  
        has = correct(x, parents)
        if has is None:
            pass
        else:
            a, b = has
            check_isinstance(a, str)
            check_isinstance(b, str)
            s = x.where.string[x.where.character:x.where.character_end]
            if not a in s:
                msg = 'Could not find piece %r in %r.' % (a, s)
                raise DPInternalError(msg)
            
            a_index = s.index(a)
            a_len = len(a) # in bytes
            a_char = x.where.character + a_index
            a_char_end = a_char + a_len
            a_where = Where(x.where.string, a_char, a_char_end)
            sub = (a_where, b)
            subs.append(sub)
            #ws_before_a = s[:a_index]
            #sub = ws_before_a + b
            #subs.append((x.where, sub))
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
