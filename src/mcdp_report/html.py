# -*- coding: utf-8 -*-
from collections import namedtuple
import os

from contracts import contract
from contracts.interface import line_and_col, location, Where
from contracts.utils import indent, raise_desc, raise_wrapped, check_isinstance
from mcdp_lang.namedtuple_tricks import isnamedtuplewhere, get_copy_with_where
from mcdp_lang.parse_actions import parse_wrap
from mcdp_lang.parts import CDPLanguage
from mcdp_lang.refinement import namedtuple_visitor_ext
from mcdp_lang.syntax import Syntax
from mcdp_lang.utils_lists import is_a_special_list
from mocdp import MCDPConstants
from mocdp.exceptions import DPSyntaxError, DPInternalError


unparsable_marker = '#@'
ATTR_WHERE_CHAR = 'c' #'where_character'
ATTR_WHERE_CHAR_END = 'ce' # where_character_end'

def isolate_comments(s):
    lines = s.split("\n")
    def isolate_comment(line):
        if '#' in line:
            where = line.index('#')
            good = line[:where]
            comment = line[where:]
            return good, comment
        else:
            return line, None

    return unzip(map(isolate_comment, lines))

def unzip(iterable):
    return zip(*iterable)

@contract(s=str, returns=str)
def ast_to_text(s):
    block = parse_wrap(Syntax.ndpt_dp_rvalue, s)[0]
    return print_ast(block)
    
@contract(s=str)
def ast_to_html(s, 
                parse_expr=None,
                
                ignore_line=None,
                add_line_gutter=True, 
                encapsulate_in_precode=True, 
                postprocess=None):
    """
        postprocess = function applied to parse tree
    """
    
    if parse_expr is None:
        raise Exception('Please add specific parse_expr (default=Syntax.ndpt_dp_rvalue)')
        
    if ignore_line is None:
        ignore_line = lambda _lineno: False
        
    original_lines = s.split('\n')

    s_lines, s_comments = isolate_comments(s)
    assert len(s_lines) == len(s_comments) 

    num_empty_lines_start = 0
    for line in s_lines:
        if line.strip() == '':
            num_empty_lines_start += 1
        else:
            break
    
    num_empty_lines_end = 0
    for line in reversed(s_lines):
        if line.strip() == '':
            num_empty_lines_end += 1
        else:
            break

    full_lines = s_lines[num_empty_lines_start: len(s_lines)- num_empty_lines_end]
    
    from mcdp_report.out_mcdpl import extract_ws
    for_pyparsing0 = "\n".join(full_lines)
    # remove also initial and final whitespace
    extra_before, for_pyparsing, extra_after = extract_ws(for_pyparsing0)
    # parse the string 'for_pyparsing'
    block0 = parse_wrap(parse_expr, for_pyparsing)[0]
    
#     print indent(recursive_print(block0), ' block0 |')
    assert isnamedtuplewhere(block0)
    # now transform everything so that it refers to s
    transform_original_s = s
    def transform(x, parents):  # @UnusedVariable
        w0 = x.where
        s0 = w0.string
        
        def translate(line, col):
            # add initial white space on first line
            if line == 0: 
                col += len(extra_before)
            # add the initial empty lines
            line += num_empty_lines_start
            return line, col
        
        # these are now in the original string transform_original_s
        line, col = translate(*line_and_col(w0.character, s0))
        character = location(line, col, transform_original_s)
        
        if w0.character_end is None:
            character_end = None
        else:
            line, col = translate(*line_and_col(w0.character_end, s0))
            character_end = location(line, col, transform_original_s) 
        
        where = Where(string=transform_original_s, 
                      character=character, 
                      character_end=character_end)
        
        return get_copy_with_where(x, where)
    
    block = namedtuple_visitor_ext(block0, transform)
    assert isnamedtuplewhere(block)

    if postprocess is not None:
        block = postprocess(block)
        if not isnamedtuplewhere(block):
            raise ValueError(block)

    snippets = list(print_html_inner(block))
    # the len is > 1 for mcdp_statements
    assert len(snippets) == 1, snippets
    snippet = snippets[0]
    transformed_p = snippet.transformed
    
#     if block.where.character != 0:
#         assert False
#         transformed_p = for_pyparsing[:block.where.character] + transformed_p

    # re-add the initial and final space here
    transformed_p = extra_before + transformed_p + extra_after
    def sanitize_comment(x):
        x = x.replace('>', '&gt;')
        x = x.replace('<', '&lt;')
        return x

    # re-add the initial and final lines
    transformed = ''
    transformed += "\n".join(s_lines[:num_empty_lines_start])
    if num_empty_lines_start:
        transformed += '\n'
    transformed +=  transformed_p
    if num_empty_lines_end:
        transformed += '\n'
    transformed += "\n".join(s_lines[len(original_lines)-num_empty_lines_end:])

     
    lines = transformed.split('\n')
    if len(lines) != len(s_comments):
        msg = 'Lost some lines while pretty printing: %s, %s' % (len(lines), len(s_comments))
        raise DPInternalError(msg) 
 
#     print('transformed', transformed)
    
    out = ""
    
    for i, (line, comment) in enumerate(zip(lines, s_comments)):
        lineno = i + 1
        if ignore_line(lineno):
            continue
        else:
#             print('line %d' % i)
#             print(' oiginal line: %r' % original_lines[i])
#             print('         line: %r' % line)
#             print('      comment: %r' % comment)
            original_line = original_lines[i]
            if comment is not None:
                assert '#' in original_line
            
            if '#' in original_line:               
                if '#' in line:
                    w = line.index('#')
                    before = line[:w] # (already transformed) #original_line[:w]
                    comment = line[w:]
                else:
                    before = line
                    comment = comment
                    
#                 print('       before: %r' % comment)
#                 print('      comment: %r' % comment)
                    
                if comment.startswith(unparsable_marker):
                    unparsable = comment[len(unparsable_marker):]
                    linec = before + '<span class="unparsable">%s</span>' % sanitize_comment(unparsable)
                else:
                    linec = before + '<span class="comment">%s</span>' % sanitize_comment(comment)
                    
            else:
                linec = line 
                
#             print('        linec: %r' % linec)
            
            if add_line_gutter:
                out += "<span class='line-gutter'>%2d</span>" % lineno
                out += "<span class='line-content'>" + linec + "</span>"
            else:
                out += linec
 
            if i != len(lines) - 1:
                out += '\n'
    
    if MCDPConstants.test_insist_correct_html_from_ast_to_html:
        from xml.etree import ElementTree as ET
        ET.fromstring(out)
        
#     print 'ast_to_html, out', out
    
    frag = ""

    if encapsulate_in_precode:
        frag += '<pre><code>'
        frag += out
        frag += '</code></pre>'
    else:
        frag += out
    
    assert isinstance(frag, str)
    
    return frag 
    

Snippet = namedtuple('Snippet', 'op orig a b transformed')

def iterate2(x):
    return iterate_(print_html_inner, x)
    
def iterate_(transform, x):
    for  _, op in iterate_notwhere(x):
        if isnamedtuplewhere(op):
            for m in transform(op):
                yield m

def order_contributions(it):
    @contract(x=Snippet)
    def loc(x):
        return x.a
    o = list(it)
    return sorted(o, key=loc)

def iterate_check_order(x, it):
    last = 0
    cur = []
    for i in it:
        op, o, a, b, _ = i
        cur.append('%s from %d -> %d: %s -> %r' % (type(x).__name__,
                                                   a, b, type(op).__name__, o))

        if not a >= last: # pragma: no cover
            raise_desc(ValueError, 'bad order', cur="\n".join(cur))
        if not b >= a: # pragma: no cover
            raise_desc(ValueError, 'bad ordering', cur="\n".join(cur))
        last = b
        yield i
        
def print_html_inner(x):
    assert isnamedtuplewhere(x), x
    
    CDP = CDPLanguage 
    if isinstance(x, CDP.Placeholder):
        orig0 = x.where.string[x.where.character:x.where.character_end]
        check_isinstance(x.label, str)
        if x.label == '...': # special case
            transformed = '…' 
        else:
            transformed = '<span class="PlaceholderLabel">⟨%s⟩</span>' % x.label
        
        yield Snippet(op=x, orig=orig0, a=x.where.character, b=x.where.character_end,
                  transformed=transformed)
        return

    subs = list(iterate_check_order(x, order_contributions(iterate2(x))))

    if is_a_special_list(x):
        for _ in subs:
            yield _
        return

    cur = x.where.character
    out = ""
    for _op, _orig, a, b, transformed in subs:
        if a > cur:
            out += sanitize(x.where.string[cur:a])
        out += transformed
        cur = b

    if cur != x.where.character_end:
        out += sanitize(x.where.string[cur:x.where.character_end])

    orig0 = x.where.string[x.where.character:x.where.character_end]

    klass = type(x).__name__

    transformed0 = ("<span class='%s' %s='%d' %s='%s'>%s</span>" 
                    % (klass, ATTR_WHERE_CHAR, x.where.character, ATTR_WHERE_CHAR_END, x.where.character_end, out))
    yield Snippet(op=x, orig=orig0, a=x.where.character, b=x.where.character_end,
                  transformed=transformed0)


def sanitize(x):
    x = x.replace('>', '&gt;')
    x = x.replace('<', '&lt;')
    return x

def print_ast(x):
    try:
        if isnamedtuplewhere(x):
            s = '%s' % type(x).__name__
            s += '  %r' % x.where
            for k, v in iterate_sub(x):
                first = ' %s: ' % k
                s += '\n' + indent(print_ast(v), ' ' * len(first), first=first)

            if x.where is None:
                raise ValueError(x)
            return s
        else:
            return x.__repr__()
    except ValueError as e:
        raise_wrapped(ValueError, e, 'wrong', x=x)



def iterate_sub(x):
    def loc(m):
        a = m[1]
        if isnamedtuplewhere(a):
            if a.where is None:
                print('warning: no where found for %s' % str(a))
                return 0
            return a.where.character
        return 0

    o = list(iterate_notwhere(x))
    return sorted(o, key=loc)


def iterate_notwhere(x):
    d = x._asdict()
    for k, v in d.items():
        if k == 'where':
            continue
        yield k, v

    
def get_css_filename(basename):
    from mcdp_library.utils.dir_from_package_nam import dir_from_package_name
    package = dir_from_package_name('mcdp_web')
    fn = os.path.join(package, 'static', 'css', basename + '.css')
    if not os.path.exists(fn):
        raise ValueError('File does not exist: %s' % fn)
    return os.path.realpath(fn)

    
def get_language_css():
    fn = get_language_css_filename()
    return open(fn).read()

def get_language_css_filename():
    return get_css_filename('compiled/mcdp_language_highlight')

def get_markdown_css_filename():
    return get_css_filename('compiled/markdown')

def get_manual_generic_css_filename():
    return get_css_filename('compiled/manual')

def get_manual_screen_css_filename():
    return get_css_filename('compiled/manual_screen')

def get_manual_print_css_filename():
    return get_css_filename('compiled/manual_prince')


def get_markdown_css():
    fn = get_markdown_css_filename()
    return open(fn).read()


def comment_out(s, line):
    lines = s.split('\n')
    lines[line+1] = unparsable_marker + lines[line+1]
    return "\n".join(lines)
    
def mark_unparsable(s0, parse_expr):
    """ Returns a tuple:
    
            s, expr, commented
            
        where:
        
            s is the string with lines that do not parse marked as "#@"
            expr is the parsed expression (can be None)
            commented is the set of lines that had to be commented out
            
        Never raises DPSyntaxError
    """
    commented = set()
    nlines = len(s0.split('\n'))
    s = s0
    while True:
        if len(commented) == nlines:
            return s, None, commented 
        try:     
            expr = parse_wrap(parse_expr, s)[0]
            return s, expr, commented
        except DPSyntaxError as e:
            line = e.where.line
            assert line is not None
            if line == nlines: # all commented
                return s, None, commented
            if line in commented:
                return s, None, commented
            commented.add(line)
            s = comment_out(s, line - 1) 
            
