# -*- coding: utf-8 -*-
from collections import namedtuple
import os
import warnings

from contracts import contract
from contracts.interface import Where
from contracts.utils import indent, raise_desc, raise_wrapped, check_isinstance
from mcdp_lang.namedtuple_tricks import isnamedtuplewhere
from mcdp_lang.parse_actions import parse_wrap
from mcdp_lang.parts import CDPLanguage
from mcdp_lang.syntax import Syntax
from mcdp_lang.utils_lists import is_a_special_list
from mocdp import logger
from mocdp.exceptions import mcdp_dev_warning, DPSyntaxError

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
def ast_to_html(s, complete_document, extra_css=None, ignore_line=None,
                add_line_gutter=True, encapsulate_in_precode=True, add_css=True,
                parse_expr=None, add_line_spans=False, postprocess=None):
    """
        postprocess = function applied to parse tree
    """
    
    if parse_expr is None:
        warnings.warn('Please add specific parse_expr (default=Syntax.ndpt_dp_rvalue)', 
                      stacklevel=2)
        parse_expr = Syntax.ndpt_dp_rvalue
        
    if add_css:
        warnings.warn('check we really need add_css = True', stacklevel=2)

    if complete_document:
        warnings.warn('please do not use complete_document', stacklevel=2)
    add_css = False

    if ignore_line is None:
        ignore_line = lambda _lineno: False
    if extra_css is None:
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

    if not isnamedtuplewhere(block):
        raise ValueError(block)

    if postprocess is not None:
        block = postprocess(block)
        if not isnamedtuplewhere(block):
            raise ValueError(block)
    

    # XXX: this should not be necessary anymore
    block2 = make_tree(block, character_end=len(s))

    snippets = list(print_html_inner(block2))
    # the len is > 1 for mcdp_statements
    assert len(snippets) == 1, snippets
    snippet = snippets[0]
    transformed_p = snippet.transformed
    # transformed_p = "".join(snippet.transformed for snippet in snippets)

    def sanitize_comment(x):
        x = x.replace('>', '&gt;')
        x = x.replace('<', '&lt;')
        return x

    transformed = '\n' * num_empty_lines_start + transformed_p
    transformed = transformed +  '\n' * num_empty_lines_end
    
    lines = transformed.split('\n')
    if len(lines) != len(s_comments): 
        msg = 'Lost some lines while pretty printing: %s, %s' % (len(lines), len(s_comments))
        logger.debug(msg)
        if len(s) > 10:
            logger.debug('original string[:10] = %r' % s[:10])
            logger.debug('original string[-10:] = %r' % s[-10:])

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
            if add_line_spans:
                out += "<span id='line%d'>" % lineno
            if add_line_gutter:
                out += "<span class='line-gutter'>%2d</span>" % lineno
                out += "<span class='line-content'>" + line + "</span>"
            else:
                out += line
            if add_line_spans:
                out += "</span>"
            if i != len(lines) - 1:
                out += '\n'

    from xml.etree import ElementTree as ET
    x = ET.fromstring(out)
    
    
    frag = ""

    if encapsulate_in_precode:
        frag += '<pre><code>'
        frag += out
        frag += '</code></pre>'
    else:
        frag += out

    if add_css:
        frag += '\n\n<style type="text/css">\n' + get_language_css() + '\n' + extra_css + '\n</style>\n\n'

    if complete_document:
        s = """<html><head>
        <meta charset="utf-8" />
        </head><body>"""
        s += frag
        s += '\n</body></html>'
        return s
    else:
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

            if not a >= last:
                raise_desc(ValueError, 'bad order', cur="\n".join(cur))
            if not b >= a:
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

@contract(character_end='int')
def make_tree(x, character_end):

    if not isnamedtuplewhere(x):
        return x
    
    if x.where is None:
        msg = 'I found an element without where attribute.'
        raise_desc(ValueError, msg, x=x)

    if x.where.character_end is not None:
        character_end = min(x.where.character_end, character_end)

    fields = {}
    last = None

    for k, v in reversed(list(iterate_sub(x))):
        if last is None:
            v_character_end = character_end
        else:
            if isnamedtuplewhere(last):
                v_character_end = last.where.character - 1
            else:
                v_character_end = character_end

        v2 = make_tree(v, character_end=v_character_end)
        fields[k] = v2
        last = v2

    w = x.where

    if w.character_end is None:
        if character_end < w.character:
            mcdp_dev_warning('**** warning: need to fix this')
            character_end = w.character + 1
        w = Where(string=w.string, character=w.character,
                  character_end=character_end)

    fields['where'] = w
    return type(x)(**fields)


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
    """ Returns
    
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
        print('nlines %s commented %s' % (nlines, commented))
        if len(commented) == nlines:
            print('looks like we commented all of it')
            return s, None, commented 
#         print s
        try:     
            expr = parse_wrap(parse_expr, s)[0]
            #expr2 = parse_ndp_refine(expr, context)
            return s, expr, commented
        except DPSyntaxError as e:
#             print e.where
#             print e
#             print ('string=%r' % s)
            line = e.where.line
            assert line is not None
            #print('found error at char %s line %s of %r: %r' % (e.where.character, line, s0, s0[e.where.character]))
            if line == nlines: # all commented
                return s, None, commented
            if line in commented:
                return s, None, commented
#                 msg = 'assertion: I already commented this line'
#                 raise_desc(AssertionError, msg, commented=commented, s=s)
            #print 'error in line %s (0 based)' % line
            commented.add(line)
            s = comment_out(s, line - 1) 
            