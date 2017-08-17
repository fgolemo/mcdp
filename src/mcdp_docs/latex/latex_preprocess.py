# -*- coding: utf-8 -*-
from contracts import contract
from mcdp import logger
from mcdp.exceptions import DPSyntaxError
from mcdp_docs.latex.latex_inside_equation_abbrevs import replace_inside_equations
from mcdp_docs.manual_constants import MCDPManualConstants
from mcdp_docs.mark.markdown_transform import is_inside_markdown_quoted_block
from mcdp_utils_misc.string_utils import get_md5
import os
import re

from contracts.interface import Where
from contracts.utils import raise_desc, raise_wrapped, check_isinstance


class LatexProcessingConstants():
    justignore = [
        'vfill', 'pagebreak', 'leavevmode', 'clearpage', 'hline',
        'hfill', 'quad', 'qquad', 'noindent',
    ]
    just_ignore_1_arg = [
        'vspace', 'vspace*', 'hspace', 'hspace*',
        'extrarowheight', 'selectlanguage',
    ]
    simplewraps = [
        ('emph', 'em', ''),
        ('textbf', 'strong', ''),
        ('footnote', 'footnote', ''),
        ('thanks', 'footnote', ''),
        ('marginpar', 'div', 'class="marginpar"'),
        ('fbox', 'div', 'class="fbox"'),
        ('uline', 'span', 'class="uline"'),
        ('F', 'span', 'class="Fcolor"'),
        ('R', 'span', 'class="Rcolor"'),
        ('I', 'span', 'class="Icolor"'),
    ]

    simples_xspace = [
        ('scottcontinuity', 'Scott continuity'),
         ('scottcontinuous', 'Scott continuous'),
         ('CPO', 'CPO'),
         ('DCPO', 'DCPO'),
         ('eg', 'e.g.'),
         ('etal', '<em>et al.</em>'),
    ]
    

def assert_not_inside(substring, s):
    if substring in s:
        i = s.index(substring)
        w = Where(s, i, i + len(substring))
        msg = 'I found the forbidden substring %r in string.' % substring
        raise DPSyntaxError(msg, where=w)

UNICODE_NBSP = u"\u00A0".encode('utf-8')


def latex_process_ignores(s):
    for j in LatexProcessingConstants.justignore:
        s = substitute_command_ext(s, j, lambda args, opts: '<!--skipped %s-->' % j,  # @UnusedVariable
                                   nargs=0, nopt=0)
    for cmd in LatexProcessingConstants.just_ignore_1_arg:
        f = lambda args, _: '<!-- skipped %s{%s} -->' % (cmd, args[0])
        s = substitute_command_ext(s, cmd, f, nargs=1, nopt=0)
    return s

def latex_process_simple_wraps(s):
    def wrap(tag, extra_attrs, s):
        return '<%s %s>%s</%s>' % (tag, extra_attrs, s,tag) 
    def justwrap(tag, extra_attrs=''):
        return lambda args, _opts: wrap(tag, extra_attrs, args[0])
    
    for cmd, tag, tagattrs in LatexProcessingConstants.simplewraps:    
        s = substitute_command_ext(s, cmd, justwrap(tag, tagattrs), nargs=1, nopt=0)
    return s

def latex_process_title(s):
    class Tmp:
        title = None
        author = None

    def find_title(args, opts):  # @UnusedVariable
        Tmp.title = args[0]
        return ''
    s = substitute_command_ext(s, "title", find_title, nargs=1, nopt=0)

    def find_author(args, opts):  # @UnusedVariable
        Tmp.author = args[0]
        return ''
    s = substitute_command_ext(s, "author", find_author, nargs=1, nopt=0)

    title = ""
    title += "<h1 class='article_title'>%s</h1>" % Tmp.title
    title += "<div class='author'>%s</div>" % Tmp.author
    s = substitute_simple(s, "maketitle", title)

    s = substitute_simple(
        s, 'and', '<span class="and" style="margin-left: 2em"></span>')

    return s

def latex_process_tilde_nbsp_and_protect_fenced(s):
    group = 'TILDETILDETILDE'
    s = s.replace('~~~', group)
    if MCDPManualConstants.activate_tilde_as_nbsp:
        s = s.replace('~', UNICODE_NBSP)
    s = s.replace(group, '~~~')
    return s

def latex_process_references(s):
    # no! let mathjax do it
    def ref_subit(m):
        x = m.group(1)
        if x.startswith('eq:'):
            return '\\ref{%s}' % x
        else:
            return '<a href="#%s" class="only-number"></a>' % x
    s = re.sub(r'\\ref{(.*?)}', ref_subit, s)

    s = substitute_command(s, 'prettyref', lambda name, inside:  # @UnusedVariable
                           '<a href="#%s"/>' % inside)

    s = re.sub(r'\\eqref{(.*?)}', r'\\eqref{eq:\1}', s)
    s = s.replace('eq:eq:', 'eq:')

    # \vref
    s = re.sub(r'\\vref{(.*?)}', r'<a class="only-number" href="#\1"></a>', s)

    s = re.sub(r'\\lemref{(.*?)}', r'<a href="#lem:\1"></a>', s)
    s = re.sub(r'\\tabref{(.*?)}', r'<a href="#tab:\1"></a>', s)
    s = re.sub(r'\\figref{(.*?)}', r'<a href="#fig:\1"></a>', s)
    s = re.sub(r'\\proref{(.*?)}', r'<a href="#pro:\1"></a>', s)
    s = re.sub(r'\\propref{(.*?)}', r'<a href="#prop:\1"></a>', s)
    s = re.sub(r'\\probref{(.*?)}', r'<a href="#prob:\1"></a>', s)
    s = re.sub(r'\\defref{(.*?)}', r'<a href="#def:\1"></a>', s)
    s = re.sub(r'\\exaref{(.*?)}', r'<a href="#exa:\1"></a>', s)
    s = re.sub(r'\\secref{(.*?)}', r'<a href="#sec:\1"></a>', s)
    s = re.sub(r'\\coderef{(.*?)}', r'<a href="#code:\1"></a>', s)
    return s

def latex_process_citations(s):
    
    def sub_cite(args, opts):
        cits = args[0].split(',')
        inside = opts[0]
        if inside is None:
            inside = ""
        res = ""
        for i, id_cite in enumerate(cits):
            inside_this = '' if i > 0 else inside
            res += '<a href="#bib:%s">%s</a>' % (id_cite, inside_this)
        return res

    s = substitute_command_ext(s, 'cite', sub_cite, nargs=1, nopt=1)
    
    return s

def latex_process_mcdp_words(s):
    for a, b in LatexProcessingConstants.simples_xspace:
        s = substitute_simple(s, a, b, xspace=True)
    return s

def latex_preprocessing(s):
    s = s.replace('\n%\n', '\n')
    s = s.replace('%\n', '\n') # inside minipage

    s = substitute_simple(s, 'textendash', '&ndash;')
    s = substitute_simple(s, 'textemdash', '&mdash;')

    s = latex_process_tilde_nbsp_and_protect_fenced(s)
    s = latex_process_ignores(s)
    s = latex_process_title(s)
    s = latex_process_references(s)
    s = latex_process_citations(s)
    s = latex_process_headers(s)

# {[}m{]}}, and we need to choose the \R{endurance~$T$~{[}s{]}}
    s = re.sub(r'{(\[|\])}', r'\1', s)




    def sub_multicolumn(args, opts):  # @UnusedVariable
        ncols, align, contents = args[:3]
        # TODO:
        return '<span multicolumn="%s" align="%s">%s</span>' % (ncols, align, contents)

    s = substitute_command_ext(
        s, 'multicolumn', sub_multicolumn, nargs=3, nopt=0)

    # note: nongreedy matching ("?" after *); and multiline (re.M) DOTALL =
    # '\n' part of .
    s = latex_process_simple_wraps(s)
    s = s.replace('\,', '&ensp;')
#     s = s.replace('%\n', '\n')

#     s = substitute_simple(s, 'etal', 'et. al.')

    s = replace_includegraphics(s) 
    s = latex_process_mcdp_words(s)

    s = substitute_simple(s, '$', '&#36;')
    s = substitute_simple(s, '#', '&#35;')
    s = substitute_simple(s, 'ldots', '&hellip;')

    s = substitute_simple(s, 'xxx', '<span class="xxx">XXX</span>')

    s = substitute_simple(s, 'centering', '<formatting class="centering"/>')

    s = substitute_simple(s, 'bigskip', '<span class="bigskip"/>')
    s = substitute_simple(s, 'medskip', '<span class="medskip"/>')
    s = substitute_simple(s, 'smallskip', '<span class="medskip"/>')
    s = substitute_simple(s, 'par', '<br class="from_latex_par"/>') 

         
#     \IEEEPARstart{O}{ne}
    s = substitute_command_ext(s, 'IEEEPARstart', lambda args, opts: args[0] + args[1],  # @UnusedVariable
                               nargs=2, nopt=0) 

    s = substitute_command_ext(s, 'url', lambda args, _: '<a href="%s">%s</a>' % (
        args[0], args[0]), nargs=1, nopt=0)  # @UnusedVariable

    # \adjustbox{max width=4.0cm}{
    # TODO:
    s = substitute_command_ext(
        s, 'adjustbox', lambda args, opts: args[1], nargs=2, nopt=0)  # @UnusedVariable

    s = replace_captionsideleft(s) 
    for x in ['footnotesize', 'small', 'normalsize']:
        s = substitute_simple(s, x,
                              '<span class="apply-parent %s"></span>' % x)  # @UnusedVariable
#         assert_not_inside('\\' + x, s)

    s = replace_environment(s, "defn", "definition", "def:")
    s = replace_environment(s, "definition", "definition", "def:")
    s = replace_environment(s, "lem", "lemma", "lem:")
    s = replace_environment(s, "lemma", "lemma", "lem:")
    s = replace_environment(s, "rem", "remark", "rem:")
    s = replace_environment(s, "remark", "remark", "rem:")
    s = replace_environment(s, "thm", "theorem", "thm:")
    s = replace_environment(s, "theorem", "theorem", "thm:")
    s = replace_environment(s, "prop", "proposition", ("pro:", "prop:"))
    s = replace_environment(s, "proposition", "proposition", ("pro:", "prop:"))
    s = replace_environment(s, "example", "example", "exa:")
    s = replace_environment(s, "proof", "proof", "proof:")
    s = replace_environment(s, "IEEEproof", "proof", "proof:")
    s = replace_environment(s, "problem", "problem", "prob:")
    s = replace_environment(s, "proposition", "proposition", "prop:")
    s = replace_environment(s, "abstract", "abstract", 'don-t-steal-label')
    s = replace_environment(s, "centering", "centering", 'don-t-steal-label')

    assert_not_inside('begin{centering}', s)
    s = replace_environment(s, "center", "center", 'don-t-steal-label')

    s = replace_environment_ext(s, "verbatim", lambda s, _: s)
    
    def lyxcode_unescape(x, opt):  # @UnusedVariable
        x = x.replace('\{', '{')
        x = x.replace('\}', '}')
        return x
        
    s = replace_environment_ext(s, "lyxcode", lyxcode_unescape) # TODO: replace ~ by ' ' 
    s = replace_environment_ext(s, "lstlisting", lambda s, _: s)
    s = replace_environment_ext(s, "quote", lambda inside, opt:  # @UnusedVariable
                                '<blockquote>' + inside + '</blockquote>')
    s = replace_environment_ext(s, "tabular", maketabular)
    s = replace_environment_ext(s, "wrapfigure", make_wrapfigure)
    s = replace_environment_ext(s, "enumerate", make_enumerate)
    s = replace_environment_ext(s, "description", make_description)
    s = replace_environment_ext(s, "itemize", make_itemize)
    s = replace_environment_ext(s, "minipage", makeminipage)
    s = replace_environment_ext(
        s, "figure", lambda inside, opt: makefigure(inside, opt, False))
    s = replace_environment_ext(
        s, "figure*", lambda inside, opt: makefigure(inside, opt, True))
    s = replace_environment_ext(
        s, "table", lambda inside, opt: maketable(inside, opt, False))
    s = replace_environment_ext(
        s, "table*", lambda inside, opt: maketable(inside, opt, True))

    s = s.replace('pro:', 'prop:')
 
    s = s.replace('{}', '')
    s = replace_quotes(s)
    return s

# def makenumerate(inside, opt):


def maketabular(inside, opt):  # @UnusedVariable
    # get alignment like {ccc}
    arg, inside = get_balanced_brace(inside)
    _align = arg[1:-1]

    SEP = '\\\\'
    inside = inside.replace('\\tabularnewline', SEP)
    rows = inside.split(SEP)
    r_htmls = []
    for r in rows:
        columns = r.split('&')
        r_html = "".join('<td>%s</td>' % _ for _ in columns)
        r_htmls.append(r_html)
    html = "".join("<tr>%s</tr>" % _ for _ in r_htmls)
    r = ""
    r += '<table>'
    r += html
    r += '</table>'
    return r


def make_wrapfigure(inside, opt):  # @UnusedVariable
    # two options
    _arg1, inside = get_balanced_brace(inside)
    _arg2, inside = get_balanced_brace(inside)

    res = makefigure(inside, opt, asterisk=False)

    res = '<div class="wrapfigure">' + res + '</div>'
    return res


def make_enumerate(inside, opt):
    return make_list(inside, opt, 'ul')


def make_itemize(inside, opt):
    return make_list(inside, opt, 'ul')


def make_list(inside, opt, name):  # @UnusedVariable
    # get alignment like {ccc}
    assert name in ['ul', 'ol']
    items = inside.split('\\item')
    items = items[1:]
    html = "".join("<li>%s</li>" % _ for _ in items)
    r = "<%s>%s</%s>" % (name, html, name)
    return r


def make_description(inside, opt):  # @UnusedVariable
    labels = []
    SEP = 'SEP'

    def found_label(args, opts):  # @UnusedVariable
        labels.append(opts[0])
        return SEP

    inside = substitute_command_ext(
        inside, 'item', found_label, nargs=0, nopt=1)

    items = inside.split(SEP)
    items = items[1:]

    html = ""
    for i, item in enumerate(items):
        if i < len(labels):
            html += '<dt>%s</dt>' % labels[i]
        html += '<dd>%s</dd>' % item

    r = "<dl>%s</dl>" % html
    return r


def maketable(inside, opt, asterisk):  # @UnusedVariable
    placement = opt  # @UnusedVariable

    class Tmp:
        label = None
        caption = None

    def sub_caption(args, opts):
        assert not opts and len(args) == 1
        Tmp.caption, Tmp.label = get_s_without_label(
            args[0], labelprefix="tab:")
        return ''

    inside = substitute_command_ext(
        inside, 'caption', sub_caption, nargs=1, nopt=0)
    assert not '\\caption' in inside

    if Tmp.label is not None:
        idpart = ' id="%s"' % Tmp.label
    else:
        idpart = ""

    if Tmp.caption is not None:
        inside = '<figcaption>' + Tmp.caption + "</figcaption>" + inside
#     print('tmp.caption: %s' % Tmp.caption)
    res = '<figure class="table"%s>%s</figure>' % (idpart, inside)

    if Tmp.label is not None:
        idpart = ' id="%s-wrap"' % Tmp.label
    else:
        idpart = ""

    res = '<div class="table-wrap"%s>%s</div>' % (idpart, res)
    return res


def makeminipage(inside, opt):
    align = opt  # @UnusedVariable
    if inside[0] == '{':
        opt_string, inside = get_balanced_brace(inside)
        latex_width = opt_string[1:-1]  # remove brace
    else:
        latex_width = None

    if latex_width is not None:
        attrs = ' latex-width="%s"' % latex_width
    else:
        attrs = ''

    res = '<div class="minipage"%s>%s</div>' % (attrs, inside)
    return res


def makefigure(inside, opt, asterisk):  # @UnusedVariable
    align = opt  # @UnusedVariable
#     print('makefigure inside = %r' % inside)

    def subfloat_replace(args, opts):
        contents = args[0]
        caption = opts[0]
        check_isinstance(contents, str)

        if caption is None:
            label = None
        else:
            caption, label = get_s_without_label(caption, labelprefix="fig:")
            if label is None:
                caption, label = get_s_without_label(
                    caption, labelprefix="subfig:")
            if label is not None and not label.startswith('subfig:'):
                msg = 'Subfigure labels should start with "subfig:"; found %r.' % (
                    label)
                label = 'sub' + label
                msg += 'I will change to %r.' % label
                logger.debug(msg)

        # we need to make up an ID
        if label is None:
            label = 'subfig:' + get_md5(contents)
#             print('making up label %r' % label)
#         if label is not None:
        idpart = ' id="%s"' % label
#         else:
#             idpart = ""

        if caption is None:
            caption = 'no subfloat caption'
        res = '<figure class="subfloat"%s>%s<figcaption>%s</figcaption></figure>' % (
            idpart, contents, caption)
        return res

    inside = substitute_command_ext(
        inside, 'subfloat', subfloat_replace, nargs=1, nopt=1)

    class Tmp:
        label = None

    def sub_caption(args, opts):
        assert not opts and len(args) == 1
        x, Tmp.label = get_s_without_label(args[0], labelprefix="fig:")
        res = '<figcaption>' + x + "</figcaption>"
#         print('caption args: %r, %r' % (args, opts))
        return res

    inside = substitute_command_ext(
        inside, 'caption', sub_caption, nargs=1, nopt=0)

#     print('makefigure inside without caption = %r'  % inside)
    assert not '\\caption' in inside

    if Tmp.label is None:
        Tmp.label = 'fig:' + get_md5(inside)
        #print('making up label %r' % Tmp.label)
#     if Tmp.label is not None:
    idpart = ' id="%s"' % Tmp.label
#     else:
#         idpart = ""

    res = '<figure%s>%s</figure>' % (idpart, inside)
    return res


def latex_process_headers(s):
    def sub_header(ss, cmd, hname, number=True):
        def replace(name, inside):  # @UnusedVariable
            options = ""
            options += ' nonumber=""' if number is False else ''
            inside, label = get_s_without_label(inside, labelprefix=None)
            options += ' id="%s"' % label if label is not None else ''
            template = '<{hname}{options}>{inside}</{hname}>'
            r = template.format(hname=hname, inside=inside, options=options)
            return r
        return substitute_command(ss, cmd, replace)

    # note that we need to do the * version before the others
    s = sub_header(s, cmd='section*', hname='h1', number=False)
    s = sub_header(s, cmd='section', hname='h1', number=True)
    s = sub_header(s, cmd='chapter*', hname='h1', number=False)
    s = sub_header(s, cmd='chapter', hname='h1', number=True)
    s = sub_header(s, cmd='subsection*', hname='h2', number=False)
    s = sub_header(s, cmd='subsection', hname='h2', number=True)
    s = sub_header(s, cmd='subsubsection*', hname='h3', number=False)
    s = sub_header(s, cmd='subsubsection', hname='h3', number=True)
    s = sub_header(s, cmd='paragraph*', hname='h4', number=False)
    s = sub_header(s, cmd='paragraph', hname='h4', number=True)
    return s


def substitute_simple(s, name, replace, xspace=False):
    """
        \ciao material-> submaterial
        \ciao{} material -> submaterial
    """
    assert not '\\' in name
    start = '\\' + name
    if not start in s:
        return s

    # points to the '{'
    istart = s.index(start)
    i = istart + len(start)

    if i >= len(s) - 1:
        is_match = True
        next_char = None
    else:
        assert i < len(s) - 1
        next_char = s[i]

        # don't match '\ciao' when looking for '\c'
        is_match = not next_char.isalpha()

    if not is_match:
        #         print('skip %s match at %r next char %r ' % (start, s[i-10:i+10], next_char))
        return s[:i] + substitute_simple(s[i:], name, replace)

    before = s[:istart]
    after = s[i:]

    if xspace:
        braces, after = possibly_eat_braces(after)
    else:
        braces, after = possibly_eat_braces(after)
        if braces:
            _spaces, after = eat_spaces(after)

    return before + replace + substitute_simple(after, name, replace)


def eat_spaces(x):
    """ x -> spaces, x' """
    j = 0
    while j < len(x) and (x[j] in [' ']):
        j += 1
    return x[:j], x[j:]


def possibly_eat_braces(remaining):
    """ x -> braces, x' """
    if remaining.startswith('{}'):
        return '{}', remaining[2:]
    else:
        return '', remaining


class Malformed(Exception):
    pass


def substitute_command_ext(s, name, f, nargs, nopt):
    """
        Subsitute \name[x]{y}{z} with 
        f : args=(x, y), opts=None -> s
        if nargs=1 and nopt = 0:
            f : x -> s
    """
#     noccur = s.count('\\'+name)
    #print('substitute_command_ext name = %s  len(s)=%s occur = %d' % (name, len(s), noccur))
    lookfor = ('\\' + name)  # +( '[' if nopt > 0 else '{')

    try:
        start = get_next_unescaped_appearance(
            s, lookfor, 0, next_char_not_word=True)
        assert s[start:].startswith(lookfor)
#         print('s[start:]  = %r starts with %r ' % (s[start:start+14], lookfor))
    except NotFound:
        #print('no string %r found' % lookfor)
        return s

    before = s[:start]
    rest = s[start:]
#     print('before: %r' % before)
    assert s[start:].startswith(lookfor)
#     print('s[start:]: %r' % s[start:])
    assert rest.startswith(lookfor)

    consume = consume0 = s[start + len(lookfor):]

    opts = []
    args = []
#     print('---- %r' % name)
#     print('consume= %r'% consume)
    for _ in range(nopt):
        consume = consume_whitespace(consume)
        if not consume or consume[0] != '[':
            #             print('skipping option')
            opt = None
        else:
            opt_string, consume = get_balanced_brace(consume)
            opt = opt_string[1:-1]  # remove brace
#             print('opt string %r consume %r opt = %r' % (opt_string, consume, opt))
        opts.append(opt)

#     print('after opts= %r'% consume)
    for _ in range(nargs):
        consume = consume_whitespace(consume)
        if not consume or consume[0] != '{':
            msg = 'Command %r: Expected {: got %r. opts=%s args=%s' % (
                name, consume[0], opts, args)
            character = start
            character_end = len(s) - len(consume)
            where = Where(s, character, character_end)
            raise DPSyntaxError(msg, where=where)
        arg_string, consume2 = get_balanced_brace(consume)
        assert arg_string + consume2 == consume
        consume = consume2
        arg = arg_string[1:-1]  # remove brace
        args.append(arg)
#     print('*')
#     print('substitute_command_ext for %r : args = %s opts = %s consume0 = %r' % (name, args, opts, consume0))
    args = tuple(args)
    opts = tuple(opts)

    replace = f(args, opts)
    if replace is None:
        msg = 'function %s returned none' % f
        raise Exception(msg)
#     nchars = len(consume0) - len(consume)
    assert consume0.endswith(consume)
#     print('consume0: %r' % consume0[:nchars])
#     print('%s %s %s -> %s ' % (f.__name__, args, opts, replace))
#     print('substitute_command_ext calling itself len(s*)=%s occur* = %d' %
#           (len(consume), consume.count('\\'+name)))
    after_tran = substitute_command_ext(consume, name, f, nargs, nopt)
    res = before + replace + after_tran
#     print('before: %r' % before)
#     print('replace: %r' % replace)
#     print('after_tran: %r' % after_tran)
#     assert not ('\\' + name ) in res, res
    return res


def consume_whitespace(s):
    while s and (s[0] in [' ']):
        s = s[1:]
    return s


def substitute_command(s, name, sub):
    """
        Subsitute \name{<inside>} with 
        sub : name, inside -> s
    """

    start = '\\' + name + '{'
    if not start in s:
        return s

    # points to the '{'
    istart = s.index(start)
    i = istart + len(start) - 1  # minus brace
    after = s[i:]
# 
    try:
        assert after[0] == '{'
        inside_plus_brace, after = get_balanced_brace(after)
    except Malformed as e:
        bit = after[:max(len(after), 15)]
        msg = 'Could not find completion for "%s".' % bit
        raise_wrapped(Malformed, e, msg)
    inside = inside_plus_brace[1:-1]
    replace = sub(name=name, inside=inside)
    before = s[:istart]
    after_tran = substitute_command(after, name, sub)
    res = before + replace + after_tran
    return res


def get_balanced_brace(s):
    """ s is a string that starts with '{'. 
        returns pair a, b, with a + b = s and 
        a starting and ending with braces
     """
    assert s[0] in ['{', '[']
    stack = []
    i = 0
    while i < len(s):
        # take care of escaping
        if s[i] == '\\' and i < len(s) - 1 and s[i + 1] in ['{', '[', '}', ']']:
            i += 2
            continue
        if s[i] == '{':
            stack.append(s[i])
        if s[i] == '[':
            stack.append(s[i])
        if s[i] == '}':
            if not stack or stack[-1] != '{':
                msg = 'One extra closing brace }'
                msg += '\n\n' + Where(s, i).__str__()
                raise_desc(Malformed, msg, stack=stack, s=s)
            stack.pop()
        if s[i] == ']':
            if not stack or stack[-1] != '[':
                msg = 'One extra closing brace ]'
                msg += '\n\n' + Where(s, i).__str__()
                raise_desc(Malformed, msg, stack=stack, s=s)
            stack.pop()

        if not stack:
            a = s[:i + 1]
            b = s[i + 1:]
            break
        i += 1
    if stack:
        msg = 'Unmatched braces at the end of s (stack = %s)' % stack
        raise_desc(Malformed, msg, s=s)
    assert a[0] in ['{', '[']
    assert a[-1] in ['}', ']']
    assert a + b == s
    return a, b


def replace_quotes(s):
    """ Replaces ``xxx'' sequences """
    START = '``'
    if not START in s:
        return s
    END = "''"
    a = s.index(START)
    if not END in s[a:]:
        return s

    b = s.index(END, a) + len(END)

    inside = s[a + len(START):b - len(END)]
    if '\n\n' in inside:
        return s
    max_dist = 200
    if len(inside) > max_dist:
        return s
    repl = '&ldquo;' + inside + '&rdquo;'
    s2 = s[:a] + repl + s[b:]
    return replace_quotes(s2)


def replace_environment_ext(s, envname, f):
    """
        f: inside, opt -> replace
    """
    # need to escape *
    d1 = '\\begin{%s}' % envname
    d2 = '\\end{%s}' % envname
    domain = 'ENVIRONMENT_%s' % envname
    subs = {}
    acceptance = None
    s = extract_delimited(s, d1, d2, subs, domain, acceptance=acceptance)
#     print('I found %d occurrences of environment %r' %  (len(subs), envname))
    for k, complete in list(subs.items()):
        assert complete.startswith(d1)
        assert complete.endswith(d2)
        inside = complete[len(d1):len(complete) - len(d2)]
#         print('%s inside %r' % (k, inside))
        assert_not_inside(d1, inside)
        assert_not_inside(d2, inside)
        if inside.startswith('['):
            opt0, inside = get_balanced_brace(inside)
            opt = opt0[+1:-1]
        else:
            opt = None
        r = f(inside, opt)
        subs[k] = r

    # recursive substitutions
    while True:
        changed = False
        for k, v in subs.items():
            if k in s:
                s = s.replace(k, v)
                changed = True
        if not changed:
            break
    return s


def replace_environment(s, envname, classname, labelprefix):
    def replace_m(inside, opt):
        #         print('replacing environment %r inside %r opt %r' % (envname, inside, opt))
        thm_label = opt
        contents, label = get_s_without_label(inside, labelprefix=labelprefix)
        if label is not None and isinstance(labelprefix, str):
            assert label.startswith(labelprefix), (s, labelprefix, label)
        id_part = "id='%s' " % label if label is not None else ""

#         print('using label %r for env %r (labelprefix %r)' % (label, envname, labelprefix))
        l = "<span class='%s_label latex_env_label'>%s</span>" % (
            classname, thm_label) if thm_label else ""
        rr = '<div %sclass="%s latex_env" markdown="1">%s%s</div>' % (
            id_part, classname, l, contents)
        return rr

    return replace_environment_ext(s, envname, replace_m)


def replace_captionsideleft(s):
    assert not 'includegraphics' in s

    def match(matchobj):
        first = matchobj.group(1)
        _first2, label = get_s_without_label(first, labelprefix="fig:")
        second = matchobj.group(2)
        if label is not None:
            idpart = ' id="%s"' % label
        else:
            idpart = ""
        res = ('<figure class="captionsideleft caption_left"%s>' % idpart)
        res += ('%s<figcaption></figcaption></figure>') % second

        return res

    s = re.sub(r'\\captionsideleft{(.*?)}{(.*?)}',
               match, s, flags=re.M | re.DOTALL)
    return s


def replace_includegraphics(s):

    #     \includegraphics[scale=0.4]{boot-art/1509-gmcdp/gmcdp_antichains_upsets}
    def match(args, opts):
        latex_options = opts[0]
        # remove [, ]
        latex_path = args[0]
        basename = os.path.basename(latex_path)
        res = '<img src="%s.pdf" latex-options="%s" latex-path="%s"/>' % (
            basename, latex_options, latex_path
        )

        return res

    s = substitute_command_ext(s, 'includegraphics', match, nargs=1, nopt=1)

#     print('after includegraphics: %r' % s)

    return s


def get_s_without_label(contents, labelprefix=None):
    """ Returns a pair s', label 
        where label could be None """
    check_isinstance(contents, str)

    class Scope:
        def_id = None

    def got_it(args, opts):  # @UnusedVariable
        found = args[0]
        if labelprefix is None:
            ok = True
        else:
            if isinstance(labelprefix, tuple):
                options = labelprefix
            elif isinstance(labelprefix, str):
                options = (labelprefix,)
            else:
                raise ValueError(labelprefix)
            ok = any(found.startswith(_) for _ in options)

        if ok:
            Scope.def_id = found
            # extract
#             print('looking for labelprefix %r found label %r in %s' % ( labelprefix, found, contents))
            return ""
        else:
            #             print('not using %r' % ( found))
            # keep
            return "\\label{%s}" % found

    contents2 = substitute_command_ext(
        contents, 'label', got_it, nargs=1, nopt=0)

    label = Scope.def_id
    if isinstance(labelprefix, str) and label is not None:
        assert label.startswith(labelprefix), (label, labelprefix)
    return contents2, label


def replace_equations(s):
    class Tmp:
        count = 0
        format = None

    def replace_eq(matchobj):
        contents = matchobj.group(1)

        def replace_label(args, opts):  # @UnusedVariable
            label = args[0]
            ss = ''
            ss += '\\label{%s}' % label
            ss += '\\tag{%s}' % (Tmp.count + 1)
            Tmp.count += 1
            return ss

        contents2 = substitute_command_ext(
            contents, 'label', replace_label, nargs=1, nopt=0)

#         contents2, label = get_s_without_label(contents, labelprefix = None)
# #         print('contents %r - %r label %r' % (contents, contents2, label))
#         if label is not None:
# #             print('found label %r' % label)

        f = Tmp.format
        s = f(Tmp(), contents2)

        return s

    # do this first
    reg = r'\$\$(.*?)\$\$'
    Tmp.format = lambda self, x: '$$%s$$' % x
    s = re.sub(reg, replace_eq, s, flags=re.M | re.DOTALL)

    reg = r'\\\[(.*?)\\\]'
    Tmp.format = lambda self, x: '$$%s$$' % x
    s = re.sub(reg, replace_eq, s, flags=re.M | re.DOTALL)

    reg = r'\\begin{equation}(.*?)\\end{equation}'
    Tmp.format = lambda self, x: '\\begin{equation}%s\\end{equation}' % x
    s = re.sub(reg, replace_eq, s, flags=re.M | re.DOTALL)

    reg = r'\\begin{align}(.*?)\\end{align}'
    Tmp.format = lambda self, x: '\\begin{align}%s\\end{align}' % x
    s = re.sub(reg, replace_eq, s, flags=re.M | re.DOTALL)

    reg = r'\\begin{align\*}(.*?)\\end{align\*}'
    Tmp.format = lambda self, x: '\\begin{align*}%s\\end{align*}' % x
    s = re.sub(reg, replace_eq, s, flags=re.M | re.DOTALL)

    reg = r'\\begin{eqnarray\*}(.*?)\\end{eqnarray\*}'
    Tmp.format = lambda self, x: '\\begin{eqnarray*}%s\\end{eqnarray*}' % x
    s = re.sub(reg, replace_eq, s, flags=re.M | re.DOTALL)

    reg = r'\\begin{eqnarray}(.*?)\\end{eqnarray}'
    Tmp.format = lambda self, x: '\\begin{eqnarray}%s\\end{eqnarray}' % x
    s = re.sub(reg, replace_eq, s, flags=re.M | re.DOTALL)

    return s


def get_next_unescaped_appearance(s, d1, search_from, next_char_not_word=False):
    while True:
        if not d1 in s[search_from:]:
            #             print('nope, no %r in s[%s:] = %r' % (d1,search_from, s[search_from:]))
            #             print('cannot find %r in s o f len = %s starting from %s' % (d1, len(s), search_from))
            raise NotFound()
        maybe = s.index(d1, search_from)
        if s[maybe - 1] == '\\':
            if 'space' in d1:
                w = Where(s, maybe, maybe + len(d1))
                msg = 'Skipping escaped sequence:\n\n' + w.__str__()
                logger.debug(msg)
#             print('found escaped match of %r (prev chars = %r)' % (d1, s[:maybe]))
            search_from = maybe + 1
        else:
            assert s[maybe:].startswith(d1)
            nextchar_i = maybe + len(d1)
            nextchar = s[nextchar_i] if nextchar_i < len(s) else 'o'
            if next_char_not_word and can_be_used_in_command(nextchar):
                #print('skipping because nextchar = %r' % nextchar)
                search_from = maybe + 1
                continue
#             print('found %r at %r ' % (d1, s[maybe:]))
            return maybe


def can_be_used_in_command(c):
    return c.isalpha() or c in ['*']


class NotFound(Exception):
    pass


@contract(returns=str)
def extract_delimited(s, d1, d2, subs, domain, acceptance=None):
    """
        acceptance: s, i -> Bool
    """
    if acceptance is None:
        acceptance = lambda _s, _i: True
    try:
        a_search_from = 0
        while True:
            a = get_next_unescaped_appearance(s, d1, a_search_from)
            if acceptance(s, a):
                break
            else:
                pass
#                 print('match of %s at %d not accepted' % (d1, a))
            a_search_from = a + 1

#         print('found delimiter start %r in %r at a = %s' %( d1,s,a))
        assert s[a:].startswith(d1)
    except NotFound:
        return s

    try:
        search_d1_from = a + len(d1)
#         print('search_d1_from = %s' % search_d1_from)
        b0 = get_next_unescaped_appearance(s, d2, search_d1_from)
        assert b0 >= search_d1_from
        assert s[b0:].startswith(d2)
        b = b0 + len(d2)
        complete = s[a:b]
    except NotFound:
        assert s[a:].startswith(d1)
#         print('could not find delimiter d2 %r in %r' % (d2, s[search_d1_from:]))
        return s

    assert complete.startswith(d1)
    assert complete.endswith(d2)

    inside = complete[len(d1):len(complete) - len(d2)]
    if True and 'begin' in d1:
        try:
            a2 = get_next_unescaped_appearance(inside, d1, 0)
            if acceptance(s, a + a2):
                #                 msg = 'Recursive %r' % d1
                #                 msg +=  '\n\n starting at (inaccurate):\n\n'+ Where(s, a).__str__()
                #                 msg +=  '\n\n inside (inaccurate):\n\n'+ Where(inside, a2).__str__()
                #

                # this is the case
                #   d1 d1 d2 d2
                #  what we want is to defer it
                start_from = a + len(d1)
                sb = s[start_from:]

                def acceptance2(string, index):  # @UnusedVariable
                    #                     assert string == sb, (string, sb)
                    return acceptance(s, index + start_from)
                sb2 = extract_delimited(
                    sb, d1, d2, subs, domain, acceptance=acceptance2)
                # now we have done
                #   d1  s2
                s0 = s[:start_from] + sb2
                return extract_delimited(s0, d1, d2, subs, domain, acceptance=acceptance)

        except NotFound:
            pass

    #inside = s[a+len(d1):b-len(d2)]
    KEYPREFIX = 'KEY' + domain
    POSTFIX = 'ENDKEY'
    key = KEYPREFIX + ('%0003d' % len(subs)) + POSTFIX
#     if KEYPREFIX in complete:
#         msg = 'recursive - %s = %r' % (key, complete)
#         msg += '\n\n'
#         def abit(s):
#             def nl(x):
#                 return x.replace('\n', ' ↵ ')
#             L = len(s)
#             if L < 80: return nl(s)
#             ss = nl(s[:min(L, 50)])
#             se = nl(s[L-min(L, 50):])
#             return ss + ' ... ' + se
#         for k in sorted(subs):
#             msg += '%r = %s\n' % (k, abit(subs[k]))
#         raise ValueError(msg)
    subs[key] = complete

#     print ('%r = %s' % (key, complete))
    s2 = s[:a] + key + s[b:]
    return extract_delimited(s2, d1, d2, subs, domain, acceptance=acceptance)


def extract_maths(s):
    """ returns s2, subs(str->str) """
    # these first, because they might contain $ $
    envs = [
        'equation', 'align', 'align*',

        # no - should be inside of $$
        'eqnarray', 'eqnarray*',

        #             'tabular' # have pesky &
    ]

    delimiters = []
    for e in envs:
        delimiters.append(('\\begin{%s}' % e, '\\end{%s}' % e))

    # AFTER the environments
    delimiters.extend([('$$', '$$'),
                       ('$', '$'),
                       ('\\[', '\\]')])

    def acceptance(s0, i):
        inside = is_inside_markdown_quoted_block(s0, i)
        return not inside

    subs = {}
    for d1, d2 in delimiters:
        s = extract_delimited(
            s, d1, d2, subs, domain='MATHS', acceptance=acceptance)

    for k, v in subs.items():
        subs[k] = replace_inside_equations(v)
    return s, subs


def extract_tabular(s):
    """ So, tabular is a special case because it uses & """

    delimiters = [('\\begin{tabular}', '\\end{tabular}')]

    def acceptance(s0, i):
        inside = is_inside_markdown_quoted_block(s0, i)
        return not inside

    subs = {}
    for d1, d2 in delimiters:
        s = extract_delimited(
            s, d1, d2, subs, domain='TABULAR', acceptance=acceptance)
    return s, subs


if __name__ == '__main__':
    s = """
For example, the expression <mcpd-value>&lt;2 J, 1 A&gt;</mcdp-value>
denotes a tuple with two elements, equal to <mcdp-value>2 J</mcpd-value>
and <code class='mcdp-value'>2 A</code>.
"""
    d1 = '<mcdp-value'
    a = get_next_unescaped_appearance(s, d1, 0)
