# -*- coding: utf-8 -*-
from collections import namedtuple
import os
import warnings

from contracts import contract
from contracts.utils import indent, raise_desc, raise_wrapped, check_isinstance
from mcdp_lang.namedtuple_tricks import isnamedtuplewhere
from mcdp_lang.parse_actions import parse_wrap
from mcdp_lang.parts import CDPLanguage
from mcdp_lang.syntax import Syntax
from mcdp_lang.utils_lists import is_a_special_list
from mocdp import MCDPConstants
from mocdp.exceptions import mcdp_dev_warning, DPSyntaxError, DPInternalError


unparsable_marker = '#@'

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
                postprocess=None,
                
                # deprecated
                complete_document=None,
                extra_css=None, 
                add_css=None,
                add_line_spans=None,):
    """
        postprocess = function applied to parse tree
    """
    
    if add_line_spans is not None and add_line_spans != False:
        warnings.warn('deprecated param add_line_spans')
    
    if parse_expr is None:
        raise Exception('Please add specific parse_expr (default=Syntax.ndpt_dp_rvalue)')
        
    if add_css is not None:
        warnings.warn('please do not use add_css', stacklevel=2)

    if complete_document is not None:
        warnings.warn('please do not use complete_document', stacklevel=2)

    if ignore_line is None:
        ignore_line = lambda _lineno: False
        
    if extra_css is not None: 
        warnings.warn('please do not use extra_css', stacklevel=2)
        
    extra_css = ''

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
    for_pyparsing = "\n".join(full_lines)
    block = parse_wrap(parse_expr, for_pyparsing)[0]

    if not isnamedtuplewhere(block): # pragma: no cover
        raise DPInternalError('unexpected', block=block)

    if postprocess is not None:
        block = postprocess(block)
        if not isnamedtuplewhere(block):
            raise ValueError(block)

    snippets = list(print_html_inner(block))
    # the len is > 1 for mcdp_statements
    assert len(snippets) == 1, snippets
    snippet = snippets[0]
    transformed_p = snippet.transformed
    
    if block.where.character != 0:
        transformed_p = for_pyparsing[:block.where.character] + transformed_p

    def sanitize_comment(x):
        x = x.replace('>', '&gt;')
        x = x.replace('<', '&lt;')
        return x

    transformed = '\n' * num_empty_lines_start + transformed_p
    transformed = transformed +  '\n' * num_empty_lines_end
    
    lines = transformed.split('\n')
    if len(lines) != len(s_comments): 
        msg = 'Lost some lines while pretty printing: %s, %s' % (len(lines), len(s_comments))
        raise DPInternalError(msg) 

    out = ""
    for i, (a, comment) in enumerate(zip(lines, s_comments)):
        line = a
        if comment:
            if comment.startswith(unparsable_marker):
                unparsable = comment[len(unparsable_marker):]
                line += '<span class="unparsable">%s</span>' % sanitize_comment(unparsable)
            else:
                line += '<span class="comment">%s</span>' % sanitize_comment(comment)
            
        lineno = i + 1
        if ignore_line(lineno):
            pass
        else:

            if add_line_gutter:
                out += "<span class='line-gutter'>%2d</span>" % lineno
                out += "<span class='line-content'>" + line + "</span>"
            else:
                out += line

            if i != len(lines) - 1:
                out += '\n'
    
    if MCDPConstants.test_insist_correct_html_from_ast_to_html:
        from xml.etree import ElementTree as ET
        ET.fromstring(out)
    
    frag = ""

    if encapsulate_in_precode:
        frag += '<pre><code>'
        frag += out
        frag += '</code></pre>'
    else:
        frag += out

    return frag 
    

Snippet = namedtuple('Snippet', 'op orig a b transformed')

def iterate2(x):
    for  _, op in iterate_notwhere(x):
        if isnamedtuplewhere(op):
            for m in print_html_inner(op):
                yield m

def order_contributions(it):
    @contract(x=Snippet)
    def loc(x):
        return x.a
    o = list(it)
    return sorted(o, key=loc)

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

    def iterate_check_order(it):
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

    subs = list(iterate_check_order(order_contributions(iterate2(x))))

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
    # special case: OpenBraceKeyword
    if out == '<':
        out = '&lt;'
    if out == '>':
        out = '&gt;'
    transformed0 = ("<span class='%s' where_character='%d' where_character_end='%s'>%s</span>" 
                    % (klass, x.where.character, x.where.character_end, out))
    yield Snippet(op=x, orig=orig0, a=x.where.character, b=x.where.character_end,
                  transformed=transformed0)

def sanitize(x):
    x = x.replace('>=', '&gt;=')
    x = x.replace('<=', '&lt;=')
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

def get_language_css():
    from mcdp_library.utils.dir_from_package_nam import dir_from_package_name
    mcdp_dev_warning('TODO: remove from mcdp_web')
    package = dir_from_package_name('mcdp_web')
    fn = os.path.join(package, 'static', 'css', 'mcdp_language_highlight.css')
    with open(fn) as f:
        css = f.read()
    return css

def get_markdown_css():
    from mcdp_library.utils.dir_from_package_nam import dir_from_package_name

    package = dir_from_package_name('mcdp_web')
    fn = os.path.join(package, 'static', 'css', 'markdown.css')
    with open(fn) as f:
        css = f.read()
    return css


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
            