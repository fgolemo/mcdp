# -*- coding: utf-8 -*-


"""
    Example usage:

        x = parse_wrap(Syntax.ndpt_dp_rvalue, s)[0]
        xr = parse_ndp_refine(x, Context())
        suggestions = get_suggestions(xr)     
        s2 = apply_suggestions(s, suggestions)


"""

from collections import namedtuple
import re

from contracts import contract
from contracts.interface import Where
from contracts.utils import check_isinstance, raise_desc
from mcdp_lang.dealing_with_special_letters import subscripts, greek_letters,\
    greek_letters_utf8
from mcdp_lang.parts import CDPLanguage
from mcdp_lang.refinement import namedtuple_visitor_ext
from mocdp import MCDPConstants
from mocdp.exceptions import DPInternalError


__all__ = [
    'get_suggestions', 
    'apply_suggestions',
]

CDP = CDPLanguage

def correct(x, parents):  # @UnusedVariable
    """ Yields a sequence of corrections.
        Each correction is either a pair (str, substitution)
        or a (Where, sub)
    """
    x_string = x.where.string[x.where.character:x.where.character_end]
    def match_in_x_string(r):
        m = re.search(r, x_string)
        return x_string[m.start():m.end()]
    
    # each of this has one element .glyph
    glyphs = {
        # CDP.leq: '≤',
        # CDP.geq: '≥',
        CDP.leq: '≼',
        CDP.geq: '≽',
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
                yield x.glyph, preferred
       
    symbols = {
        CDP.Nat: 'ℕ',
        CDP.Int: 'ℤ',
        CDP.Rcomp: 'ℝ',
    }     
    
    for klass, preferred in symbols.items():
        if isinstance(x, klass):
            if x.symbol != preferred:
                yield x.symbol, preferred
        
    keywords = {
        CDP.TopKeyword: '⊤',
        CDP.BottomKeyword: '⊥',
        CDP.FinitePosetKeyword: 'poset',
    }
    
    for klass, preferred in keywords.items():
        if isinstance(x, klass):
            if x.keyword != preferred:
                yield x.keyword, preferred

    
    if isinstance(x, CDP.NewFunction) and x.keyword is None:
        name = x.name.value
        yield name, 'provided %s' % name
    
    if isinstance(x, CDP.NewResource) and x.keyword is None:
        name = x.name.value
        yield name, 'required %s' % name
    
    if isinstance(x, CDP.Resource) and isinstance(x.keyword, CDP.DotPrep):
        dp, s = x.dp.value, x.s.value
        r = '%s.*\..*%s' % (dp, s)
        old = match_in_x_string(r)
        new = '%s required by %s' % (s, dp)
        yield old, new
    
    if isinstance(x, CDP.Function) and isinstance(x.keyword, CDP.DotPrep):
        dp, s = x.dp.value, x.s.value
        r = '%s.*\..*%s' % (dp, s)
        old = match_in_x_string(r)
        new = '%s provided by %s' % (s, dp)
        yield old, new
    
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
                yield x_string, s2
            
            w = '^ ' + n
            if w in x_string:
                s2 = x_string.replace(w, replacement)
                yield x_string, s2

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
                        yield w, replacement
                    
    if isinstance(x, (CDP.VName, CDP.RName, CDP.FName, CDP.CName)):
        suggestion = get_suggestion_identifier(x_string)
        if suggestion is not None:
            yield suggestion
        
    if isinstance(x, CDP.BuildProblem):
#         print 'build', x_string.__repr__()
        for _ in suggestions_build_problem(x):
            yield _
            
def suggestions_build_problem(x):
    x_string = x.where.string[x.where.character:x.where.character_end]
    offset = x.where.character
    #print 'build complete %d  %r' %(offset, x.where.string)
    TOKEN = 'mcdp'
    first_appearance_mcdp_in_sub = x_string.index(TOKEN)
    first_appearance_mcdp_in_orig = offset + first_appearance_mcdp_in_sub
    first_line = x.where.string[:first_appearance_mcdp_in_orig+len(TOKEN)].split('\n')[-1]
    
#         print 'first line: %r' % that_line
    token_distance_from_newline = first_line.index(TOKEN) 
    rest_of_first_line = first_line[token_distance_from_newline+len(TOKEN):]
    if TOKEN in rest_of_first_line:
        msg = 'I cannot deal with two "mcdp" in the same line.'
        raise_desc(NotImplemented, msg, that_line=first_line)
    # no! initial_spaces =  count_initial_spaces(that_line)
#         print('initial spaces = %d' % initial_spaces)
#         print
    # now look for all the new lines later
    INDENT = MCDPConstants.indent
    TABSIZE = MCDPConstants.tabsize
    
    # a string containing all complete lines including xstring

    before = x.where.string[:first_appearance_mcdp_in_orig]
    if '\n' in before:
        last_newline_before = list(findall('\n', before))[-1] + 1
    else:
        last_newline_before = 0
        
    rbrace = x.rbrace.where.character
    # string after the rbrace
    after = x.where.string[rbrace+1:]
    if '\n' in after:
        first_newline_after = list(findall('\n', after))[0] #- 1
        first_newline_after += rbrace + 1 
    else:
        first_newline_after = len(x.where.string)
    
    lines_containing_xstring_offset = last_newline_before
    lines_containing_xstring = x.where.string[lines_containing_xstring_offset:first_newline_after]
#     print()
#     print()
#     print('original string: %r' % x.where.string)
#     print('x_string: %r' % x_string)
#     print('after : %r' % after)
#     print('lines_containing_xstring: %r' % lines_containing_xstring)
    # iterate over the lines 
    line_infos = list(iterate_lines(lines_containing_xstring, lines_containing_xstring_offset))
    
    
    initial_spaces = count_initial_spaces(line_infos[0].line_string, TABSIZE)
    for line_info in line_infos:
#         print(' --- line %s' % str(line_info))
        i = line_info.character
        that_line = line_info.line_string
        
        assert that_line == x.where.string[line_info.character:line_info.character_end]
        
#             print('%d its line: %r' % (i, that_line))
        # not the last with only a }
        
        # index of current line start in global string
        contains_rbrace = line_info.character <= rbrace < line_info.character_end
#         print 'that_line = %r' % (that_line) 
#         print ('rbrace pos %r' % rbrace)
        if contains_rbrace:
            assert '}' in that_line
            align_at = initial_spaces
            before_rbrace = x.where.string[line_info.character:rbrace]
            before_rbrace_is_ws = is_all_whitespace(before_rbrace)
            
            if not before_rbrace_is_ws:
                # need to add a newline
#                 print('adding newline before rbrace')
                w = Where(x.where.string, rbrace, rbrace)
                replace = '\n' + ' ' * align_at
                yield w, replace
                continue
    
        is_line_with_initial_mcdp = (line_info.character <=  
                first_appearance_mcdp_in_orig < line_info.character_end)
        if is_line_with_initial_mcdp: 
#                 print('skip because first') 
            continue

        if contains_rbrace:
            align_at = initial_spaces
        else:
            align_at = initial_spaces + INDENT
        
        nspaces = count_initial_spaces(that_line, TABSIZE)
#         print('has spaces %d' % nspaces)
        if nspaces < align_at: 
            # need to add some indentation at beginning of line
            w = Where(x.where.string, i, i)
            to_add = align_at - nspaces
            remaining = ' ' * to_add
#             print('add %d spaces' % to_add)
            yield w, remaining 
        if nspaces > align_at:
            remove = nspaces - align_at
            # XXX this should not include tabs... FIXME
            w = Where(x.where.string, i, i + remove)
#             print('remove %d spaces' % remove)
            yield w, ''
        
        if TOKEN in that_line:
            break
            
LineInfo = namedtuple('LineInfo', 'line_string character character_end')

def iterate_lines(s, offset):
    # iterate over the lines, yields LineInfo
    lines = s.split('\n')
    sofar = 0

    for line_string in lines:
        l = len(line_string)
        character = offset + sofar
        character_end = character + l
#         
#         if line_string != s[character-offset:character_end-offset]:
#             print 'error'
#             print 'lines', lines
#             print 'sofar', sofar
#             print 'portion', s[character:character_end]
#             print 'line_string', line_string
            
        assert line_string == s[character-offset:character_end-offset]
        yield LineInfo(line_string, character, character_end)
        sofar += l + 1 # newline

def is_all_whitespace(s):
    """ Returns true if the string is all whitespace (space or '\t') """
    ws = [' ', '\t']
    return all(c in ws for c in s)

def count_initial_spaces(x, tabsize):
    from mcdp_report.out_mcdpl import extract_ws
    first, _middle, _last = extract_ws(x)
    n = 0
    for s in first:
        if s == ' ':
            n += 1
        if s == '\t':
            n += tabsize
    return n

def findall(p, s):
    '''Yields all the positions of
    the pattern p in the string s.'''
    i = s.find(p)
    while i != -1:
        yield i
        i = s.find(p, i+1)

@contract(s=bytes, returns='tuple')
def get_suggestion_identifier(s):
    """ Returns a pair of (what, replacement), or None if no suggestions available""" 
    check_isinstance(s, bytes)
    for num, subscript in subscripts.items():
        s0 = '_%d' % num
        if s.endswith(s0):
            return s0, subscript.encode('utf8')
    for name, letter in greek_letters_utf8.items():
        
        if name in s or name == s:
            print(name, letter, s)
            # yes: 'alpha_0'
            # yes: 'alpha0'
            # no: 'alphabet'
            i = s.index(name)
            letter_before = None if i == 0 else s[i-1:i]
            a = i + len(name)
            print a, i, len(s)
            letter_after = None if a == len(s)  else s[a:a+1]
            
            dividers = ['_','0','1','2','3','4','5','6','7','8','9']
            ok1 = letter_before is None or letter_before in dividers
            ok2 = letter_after is None or letter_after in dividers
            print (letter_before, letter_after)
            print(ok1, ok2)
            if ok1 and ok2:
                return name, letter
    return None
    
def get_suggestions(xr):
    """ Returns a sequence of (where, replacement_string) """
    subs = [] # (where, sub)
    def find_corrections(x, parents):
        # expect an iterator  
        s = x.where.string[x.where.character:x.where.character_end]
        
        for suggestion in correct(x, parents):
            a, b = suggestion
            if isinstance(a, str):
                if not a in s:
                    msg = 'Could not find piece %r in %r.' % (a, s)
                    raise DPInternalError(msg)
                a_index = s.index(a)
                a_len = len(a) # in bytes
                a_char = x.where.character + a_index
                a_char_end = a_char + a_len
                a_where = Where(x.where.string, a_char, a_char_end)
            else:
                check_isinstance(a, Where)
                a_where = a
            
            check_isinstance(b, str)
            
            sub = (a_where, b)
            subs.append(sub) 
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
    
    # do first the ones that are insertions
    def order(s):
        where, _ = s
        return where.character_end - where.character    
    
    for where, replacement in sorted(subs, key=order):
        assert where.string == s, (where.string, s)
        # print ('replace %d to %d with %r' % (where.character, where.character_end, replacement))
        # list of indices of characters to remove
        seq = list(range(where.character, where.character_end))
        
        # offset = chars.index(seq[0])
        if where.character not in chars:
            msg = 'Oops, char %d not in %s' % (where.character, chars)
            raise NotImplemented(msg)
        offset = chars.index(where.character)

        for _ in seq:
            chars.remove(_)
            
        for j, c in enumerate(replacement):
            cid = len(id2char)
            id2char[cid] = c 
            chars.insert(offset + j, cid)
    
    result = ''.join(id2char[_] for _ in chars)
    return result
