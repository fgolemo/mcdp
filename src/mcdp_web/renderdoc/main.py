# -*- coding: utf-8 -*-
from contracts import contract
from contracts.utils import raise_desc, indent
from mcdp_library import MCDPLibrary
from mcdp_web.renderdoc.highlight import mark_console_pres,\
    escape_for_mathjax, make_figure_from_figureid_attr
from mcdp_web.renderdoc.latex_preprocess import latex_preprocessing

from .highlight import html_interpret
from .markd import render_markdown
from .prerender_math import prerender_mathjax
from mcdp_web.renderdoc.xmlutils import check_html_fragment
from mocdp.exceptions import DPInternalError


__all__ = ['render_document']

@contract(returns='str', s=str, library=MCDPLibrary, raise_errors=bool)
def render_complete(library, s, raise_errors, realpath, generate_pdf=False):
    """
        Transforms markdown into html and then renders the mcdp snippets inside.
        
        s: a markdown string with embedded html snippets
        
        Returns an HTML string; not a complete document.
    """
    if isinstance(s, unicode):
        msg = 'I expect a str encoded with utf-8, not unicode.'
        raise_desc(TypeError, msg, s=s)


    
    # copy all math content,
    #  between $$ and $$
    #  between various limiters etc.
    # returns a dict(string, substitution)
    s, maths = extract_maths(s) 
    print('maths = %s' % maths)
    
    # fixes for LaTeX
    s = latex_preprocessing(s)
    
    s = '<div style="display:none">Because of mathjax bug</div>\n\n\n' + s

    # cannot parse html before markdown, because md will take
    # invalid html, (in particular '$   ciao <ciao>' and make it work)
    
    
    s = s.replace('\\\\', 'MATHJAX_BARBAR')
    s = s.replace('*}', '\*}')
    def markdown_fixes(l):
        l = replace_backticks_except_in_backticks_expression(l)
        l = replace_underscore_etc_in_formulas(l)
        return l

    s = s.replace('<mcdp-poset>', '<mcdp-poset markdown="0">')
    print(indent(s, 'before markdown | '))
    
        
    s = render_markdown(s)
    
    print(indent(s, 'after  markdown | '))

    for k,v in maths.items():
        if not k in s:
            msg = 'Cannot find %r (= %r)' % (k, v)
            raise_desc(DPInternalError, msg, s=s)
        def preprocess_equations(x):
            # this gets mathjax confused
            x = x.replace('>', '\\gt')
            x = x.replace('<', '\\lt')
            return x
            
        v = preprocess_equations(v)
        s = s.replace(k, v)

    from mcdp_web.renderdoc.latex_preprocess import replace_equations
    s = replace_equations(s)        
    s = s.replace('\\*}', '*}')
    
#     s = s.replace('MATHJAX_BARBAR', '\\\\')

    s = replace_underscore_etc_in_formulas_undo(s)
    
#     print(indent(s, 'after  replace | '))
        
    # this escapes $ to DOLLAR
    print(indent(s, 'before  mathjax | '))
    s = escape_for_mathjax(s)

    check_html_fragment(s)
#     print(indent(s, 'before prerender_mathjax | '))
    # mathjax must be after markdown because of code blocks using "$"
    s = prerender_mathjax(s)
    
    check_html_fragment(s)
    
#     print(indent(s, 'after prerender_mathjax | '))
    
#     print(indent(html, 'after render_markdown'))

    html = s
    html = html.replace('<p>DRAFT</p>', '<div class="draft">')
    
    html = html.replace('<p>/DRAFT</p>', '</div>')
    
    html = mark_console_pres(html)
    html = make_figure_from_figureid_attr(html)
    check_html_fragment(html)
    html2 = html_interpret(library, html, generate_pdf=generate_pdf,
                           raise_errors=raise_errors, realpath=realpath)

    check_html_fragment(html2)
    from mcdp_report.gg_utils import embed_images_from_library
    html3 = embed_images_from_library(html=html2, library=library)
    
    check_html_fragment(html3) 
    
    
    
    return html3

def get_mathjax_preamble():
    
    symbols = '/Users/andrea/env_mcdp/src/mcdp/libraries/manual.mcdplib/symbols.tex'
    tex = open(symbols).read()
    
    lines = tex.split('\n')
    lines = ['$%s$' % l for l in filter(lambda x: len(x.strip())>0, lines)]
    tex = "\n".join(lines)
    frag = '<div class="mathjax-symbols">%s</div>\n' % tex
    frag = tex
    return frag

def extract_maths(s):
    """ returns s2, subs(str->str) """
    delimiters = [('$$','$$'),
                    ('$','$'),
                   ('\\[', '\\]')]
    envs = ['equation','align','align*','eqnarray','eqnarray*']
    for e in envs:
        delimiters.append(('\\begin{%s}' % e, '\\end{%s}'% e))
    
    subs = {}
    for d1, d2 in delimiters:
        from mcdp_web.renderdoc.latex_preprocess import extract_delimited
        s = extract_delimited(s, d1, d2, subs)  
    return s, subs

def replace_markdown_line_by_line(s, line_transform):    
    lines = s.split('\n')
    block_started = False
    for i in range(len(lines)):
        l = lines[i]
        if l.startswith('~~~'):
            if block_started:
                block_started = False
                continue
            else:
                block_started = True
            
        if block_started:
            continue
        is_literal = l.startswith(' '*4)
        if is_literal: continue
        l2 = line_transform(l)
        lines[i] = l2
    s2 = "\n".join(lines)

    return s2
# 
# def replace_backticks_except_in_backticks_expression(l):
#     D = 'DOUBLETICKS'
#     l = l.replace('``', D)
#     tokens = l.split(D)
#     tokens2 = []
#     for j, f in enumerate(tokens):
#         if j % 2 == 0: # outside the quotes
#             f = f.replace('`', '&#96;')
#         tokens2.append(f)
#     l2 = D.join(tokens2)
#     # now re-replace the doubleticks
#     l2 = l2.replace(D, '``')
#     return l2

def replace_backticks_except_in_backticks_expression(l):
    def inside(sf):
        sf = sf.replace('`', '&#96;')
        return sf
    def outside(sf):
        return sf
    return replace_inside_delims(l, '$', inside=inside, outside=outside)

def replace_inside_delims(l, delim, inside, outside):
    D = 'DELIM'
    l = l.replace(delim, D)
    tokens = l.split(D)
    tokens2 = []
    for j, f in enumerate(tokens):
        if j % 2 == 0: # outside the quotes
            f = outside(f)
        else:
            f = inside(f)
        tokens2.append(f)
    l2 = D.join(tokens2)
    # now re-replace the doubleticks
    l2 = l2.replace(D, delim)
    return l2

UNDERSCORE_IN_FORMULA = 'UNDERSCOREINFORMULA'
STAR_IN_FORMULA = 'STARINFORMULA'

def replace_underscore_etc_in_formulas(l):
    """ Replace the special characters in the formulas """
    def inside(sf):
        sf = sf.replace('_', UNDERSCORE_IN_FORMULA)
        sf = sf.replace('*', STAR_IN_FORMULA)
        sf = sf.replace('\\', '\\\\')
        return sf
    def outside(sf):
        return sf
    l = replace_inside_delims(l, '$', inside=inside, outside=outside)
    return l
    
def replace_underscore_etc_in_formulas_undo(s):
    s = s.replace(UNDERSCORE_IN_FORMULA, '_')
    s = s.replace(STAR_IN_FORMULA, '*')
    return s

