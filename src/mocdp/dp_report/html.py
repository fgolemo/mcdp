from collections import namedtuple
from contracts import contract
from contracts.interface import Where
from contracts.utils import indent, raise_desc, raise_wrapped
from mocdp.lang.namedtuple_tricks import isnamedtuplewhere
from mocdp.lang.parse_actions import parse_wrap

from mocdp.lang.syntax import Syntax
from mocdp.lang.utils_lists import is_a_special_list


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
def ast_to_html(s, complete_document, extra_css="", ignore_line=lambda _lineno: False):

    s_lines, s_comments = isolate_comments(s)
    assert len(s_lines) == len(s_comments) 
    # Problem: initial comment, '# test connected\nmcdp'

    empty_lines = []
    for line in s_lines:
        if line.strip() == '':
            empty_lines.append(line)
        else:
            break

    full_lines = s_lines[len(empty_lines):]
    for_pyparsing = "\n".join(full_lines)
    block = parse_wrap(Syntax.ndpt_dp_rvalue, for_pyparsing)[0]

    if not isnamedtuplewhere(block):
        raise ValueError(block)

    # print print_ast(block)
    # XXX: this should not be necessary anymore
    block2 = make_tree(block, character_end=len(s))
    # print print_ast(block2)

    snippets = list(print_html_inner(block2))
    assert len(snippets) == 1
    snippet = snippets[0]

    def sanitize_comment(x):
        x = x.replace('>', '&gt;')
        x = x.replace('<', '&lt;')
        return x

    transformed_p = (snippet.transformed)

    # add back the white space
    if empty_lines:
        transformed = "\n".join(empty_lines) + '\n' + transformed_p
    else:
        transformed = transformed_p
    
    lines = transformed.split('\n')
    if len(lines) != len(s_comments):
#         for i in range(min(len(lines), len(s_comments))):
#
#             print('orig %d: %s' % (i, s_lines[i]))
#             print('trans %d: %s' % (i, lines[i]))
        msg = 'Lost some lines while pretty printing: %s, %s' % (len(lines), len(s_comments))
        print(msg)
        if len(s) > 10:
            print('original string[:10] = %r' % s[:10])
            print('original string[-10:] = %r' % s[-10:])
    
    out = ""
    for i, (a, comment) in enumerate(zip(lines, s_comments)):
        line = a
        if comment:
            line += '<span class="comment">%s</span>' % sanitize_comment(comment)
        lineno = i + 1
        if ignore_line(lineno):
            pass
        else:
            out += "<span id='line%d'>" % lineno
            out += "<span class='line-gutter'>%2d</span>" % lineno
            out += "<span class='line-content'>" + line + "</span>"
            out += "</span>"
            if i != len(lines) - 1:
                out += '\n'

    frag = ""

    frag += '\n<pre><code>'
    frag += out
    frag += '\n</code></pre>'

    frag += '\n\n<style type="text/css">\n' + css + '\n' + extra_css + '\n</style>\n\n'

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
    transformed0 = "<span class='%s'>%s</span>" % (klass, out)
    yield Snippet(op=x, orig=orig0, a=x.where.character, b=x.where.character_end,
                  transformed=transformed0)

def sanitize(x):
    if 'span' in x:
        raise ValueError('getting confused %s' % x)

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
            print('**** warning: need to fix this')
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


css = """ 
     span.ProvideKeyword, span.FName { color: darkgreen;}
     span.RequireKeyword, span.RName  { color: darkred;}
     
     span.NewResource { color: darkred;}
     span.NewFunction { color: darkgreen; }
     
    span.Unit, span.Nat, span.Int  {  color: #aC5600 ;}
    span.ValueExpr { color: #CC6600 ;}
     
     /*span.Function  { color: darkgreen;}*/
    span.ProvideKeyword,
    span.RequireKeyword,     
    span.MCDPKeyword,
    span.SubKeyword,
    span.CompactKeyword,
    span.AbstractKeyword,
    span.TemplateKeyword,
    span.ForKeyword,
    span.UsingKeyword,
    span.RequiredByKeyword,
    span.ProvidedByKeyword,
    span.LoadKeyword,
    span.CodeKeyword,
    span.leq, span.geq, span.OpKeyword, span.eq, span.plus, span.times, span.DPWrapToken,
    span.ImplementedbyKeyword , span.FromCatalogueKeyword, span.MCDPTypeKeywor,
    span.InstanceKeyword,
    span.MCDPTypeKeyword { 
        font-weight: bold; 
    }
       
    span.ImpName { color: #CC6600; }
    span.FuncName { color: #CC6600 ; }

    span.MCDPKeyword,
    span.SubKeyword,
    span.CompactKeyword,
    span.AbstractKeyword,
    span.TemplateKeyword,
    span.ForKeyword,
    span.UsingKeyword,
    span.RequiredByKeyword,
    span.ProvidedByKeyword,
    span.LoadKeyword, span.CodeKeyword,
    span.leq, span.geq, span.OpKeyword, span.eq, span.plus, span.times, span.DPWrapToken,
    span.ImplementedbyKeyword,  
    span.FromCatalogueKeyword, 
    span.MCDPTypeKeyword,
    span.InstanceKeyword
    {
       color: #00a;
    }
    
    span.FName, span.RName { } 
    span.DPName {  
        color: #a0a;
    }
    
    span.DPTypeName, span.DPVariableRef { 
        color:  #00F; 
        font-weight: bold; 
    }
      
    span.comment { 
        color: grey;
    }

    span.line-gutter {    
        margin-right: 1em; 
        color: grey; 
    }
"""
