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
from mcdp_lang.dealing_with_special_letters import\
    greek_letters_utf8, subscripts_utf8, ends_with_divider,\
    starts_with_divider, digit2superscript
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
        # name = x.name.value # no! name is interpreted (expanded) 
        name = x.name.where.get_substring()
        yield name, 'provided %s' % name
    
    if isinstance(x, CDP.NewResource) and x.keyword is None:
        # name = x.name.value # no! name is interpreted (expanded) 
        name = x.name.where.get_substring()
        yield name, 'required %s' % name
    
    if isinstance(x, CDP.Resource) and isinstance(x.keyword, CDP.DotPrep):
        dp, s = x.dp.where.get_substring(), x.s.where.get_substring()
        r = '%s.*\..*%s' % (dp, s)
        old = match_in_x_string(r)
        new = '%s required by %s' % (s, dp)
        yield old, new
    
    if isinstance(x, CDP.Function) and isinstance(x.keyword, CDP.DotPrep):
        dp, s = x.dp.where.get_substring(), x.s.where.get_substring()
        r = '%s.*\..*%s' % (dp, s)
        old = match_in_x_string(r)
        new = '%s provided by %s' % (s, dp)
        yield old, new
    
    if isinstance(x, CDP.RcompUnit):
        for n, replacement in digit2superscript.items():
            w = '^' + n
            if w in x_string:
                s2 = x_string.replace(w, replacement)
                yield x_string, s2
            
            w = '^ ' + n
            if w in x_string:
                s2 = x_string.replace(w, replacement)
                yield x_string, s2

    if isinstance(x, CDP.PowerShort):
        for n, replacement in digit2superscript.items():
            for i in reversed(range(3)):
                for j in reversed(range(3)):
                    w = ' ' * i + '^' + ' ' * j + n
                    if w in x_string:
                        yield w, replacement
                    
    if isinstance(x, (CDP.VName, CDP.RName, CDP.FName, CDP.CName)):
        value_string = x_string.strip()
        # This is not always true --- sometimes whitespace is included
        # eventually, when ow is everywhere (or similar mechanism)
        # we can assume that x_string == value_string
        # value_string = x.value
        # if not value_string in x_string:
        #     msg = 'Something fishy'
        #     raise_desc(DPInternalError, msg, x_string=x_string, value_string=value_string)
        suggestion = get_suggestion_identifier(value_string)
        if suggestion is not None:
            print('got suggestion %s for %s (col %s:%s)' % (suggestion, x, x.where.line, x.where.col))
            yield suggestion
        
    if isinstance(x, CDP.BuildProblem):
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
        
def get_suggested_identifier(s0):
    """ Returns the suggested form of the identifier """
    suggestion = get_suggestion_identifier(s0)
    if suggestion is None:
        return s0
    else:
        what, replacement = suggestion
        return s0.replace(what, replacement)
 
@contract(s0=bytes, returns='None|tuple')
def get_suggestion_identifier(s0):
    """ Returns a pair of (what, replacement), or None if no suggestions available"""
    if s0 != s0.strip():
        msg = 'This is not an identifier: %r' % s0
        raise ValueError(msg)
    #print('get_suggestion_identifier(%s)' % s0)
    suggestions = []
    s = s0
    while True:
        suggestion = get_suggestion_identifier0(s)
        
        if suggestion is None: 
            break
        
        suggestions.append(suggestion)
        
        # TODO: check only one match
        i, what, replacement = suggestion
        # check it is correct
        sub = s[i:i+len(what)]
        assert sub == what, (sub, what)
        s = s[:i] + replacement + s[i+len(what):]
        
    #print('suggestions: %s  s: %r  s0: %r' % (suggestions, s, s0))
    if not suggestions:
        return None
    elif len(suggestions) == 1:
        return suggestions[0].what, suggestions[0].replacement
    else:
        return s0, s   
        
IdentifierSuggestion = namedtuple('IdentifierSuggestion', 'i what replacement')

@contract(s=bytes, returns='None|$IdentifierSuggestion')
def get_suggestion_identifier0(s):
    """ Returns a tuple of (index, what, replacement), or None if no suggestions available""" 
    check_isinstance(s, bytes)
    for num, subscript in subscripts_utf8.items():
        s0 = '_%d' % num
        if s.endswith(s0):
            i = len(s) - 2
            x = IdentifierSuggestion(i=i, what=s0[-2:], replacement=subscript)
            assert s[x.i:].startswith(x.what), (s[x.i:], x.what)
            return x
    
    for name, letter in greek_letters_utf8.items():
        for m in re.finditer(name, s):
            i = m.start(0)
            assert s[i:].startswith(name)
            # yes: 'alpha_0'
            # yes: 'alpha0'
            # no: 'alphabet'
            after = s[i + len(name):]
            before = s[:i]
            ok1 = after == '' or starts_with_divider(after)
            ok2 = before == '' or ends_with_divider(before)
            if ok1 and ok2:
                return IdentifierSuggestion(i=i, what=name, replacement=letter)
            else:
                pass
                #print('skipping present %r for %s %s' % (name, ok1,ok2) )
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
                    msg = 'Invalid suggestion %s. Could not find piece %r in %r.' % (suggestion, a, s)
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
