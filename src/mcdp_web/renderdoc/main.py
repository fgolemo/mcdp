# -*- coding: utf-8 -*-
from contracts import contract
from contracts.utils import raise_desc, indent
from mcdp_library import MCDPLibrary
from mcdp_web.renderdoc.abbrevs import other_abbrevs
from mcdp_web.renderdoc.highlight import fix_subfig_references
from mcdp_web.renderdoc.latex_preprocess import extract_maths
from mcdp_web.renderdoc.macro_col2 import col_macros,\
    col_macros_prepare_before_markdown
from mcdp_web.renderdoc.markdown_transform import is_inside_markdown_quoted_block
from mcdp_web.renderdoc.preliminary_checks import do_preliminary_checks_and_fixes
from mocdp.exceptions import DPInternalError

from .highlight import html_interpret,  mark_console_pres,\
    escape_for_mathjax, make_figure_from_figureid_attr
from .latex_preprocess import latex_preprocessing
from .markd import render_markdown
from .prerender_math import prerender_mathjax
from .xmlutils import check_html_fragment
from mocdp import logger


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

   
    s = do_preliminary_checks_and_fixes(s)
    
    # copy all math content,
    #  between $$ and $$
    #  between various limiters etc.
    # returns a dict(string, substitution)
    s, maths = extract_maths(s) 
    print('maths = %s' % maths)
    for k, v in maths.items():
        if v[0] == '$' and v[1] != '$$':
            if '\n\n' in v:
                msg = 'Suspicious math fragment %r = %r' % (k, v)
                logger.error(maths)
                logger.error(msg)
                raise ValueError(msg)
    
    # fixes for LaTeX
    s = latex_preprocessing(s)
    
    s = '<div style="display:none">Because of mathjax bug</div>\n\n\n' + s

    # cannot parse html before markdown, because md will take
    # invalid html, (in particular '$   ciao <ciao>' and make it work)
    
    s = s.replace('*}', '\*}')
#     def markdown_fixes(l):
#         l = replace_backticks_except_in_backticks_expression(l)
#         l = replace_underscore_etc_in_formulas(l)
#         return l


    s, mcdpenvs = protect_my_envs(s) 
#     print('mcdpenvs = %s' % maths)

    s = col_macros_prepare_before_markdown(s)
    
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
#             print('replaced equation %r by %r ' % (x0, x))
            return x
            
        v = preprocess_equations(v)
        s = s.replace(k, v)

    from mcdp_web.renderdoc.latex_preprocess import replace_equations
    s = replace_equations(s)        
    s = s.replace('\\*}', '*}')
    
#     s = replace_underscore_etc_in_formulas_undo(s)
    
#     print(indent(s, 'after  replace | '))
        

#     print(indent(s, 'before  mathjax | '))
    


    s = escape_for_mathjax(s)

    check_html_fragment(s)
#     print(indent(s, 'before prerender_mathjax | '))
    # mathjax must be after markdown because of code blocks using "$"
    s = prerender_mathjax(s)

    for k,v in mcdpenvs.items():
        # there is this case:
        # ~~~
        # <pre> </pre>
        # ~~~
        s = s.replace(k, v)

    check_html_fragment(s)
    
#     print(indent(s, 'after prerender_mathjax | '))
    

    s = s.replace('<p>DRAFT</p>', '<div class="draft">')
    
    s = s.replace('<p>/DRAFT</p>', '</div>')
    
    s = mark_console_pres(s)
    s = make_figure_from_figureid_attr(s)
    
    s = col_macros(s)
    s = other_abbrevs(s)
#     print(indent(s, 'after  col_macros | '))
    s = fix_subfig_references(s)
    check_html_fragment(s)
    
#     print(indent(s, 'before  html_interpret | '))
    s = html_interpret(library, s, generate_pdf=generate_pdf,
                           raise_errors=raise_errors, realpath=realpath)

    check_html_fragment(s)
    from mcdp_report.gg_utils import embed_images_from_library
    
    raise_missing_image_errors = False
    s = embed_images_from_library(html=s, library=library, 
                                      raise_errors=raise_missing_image_errors)
    
    check_html_fragment(s) 
    
    return s

def get_mathjax_preamble():
    
    symbols = '/Users/andrea/env_mcdp/src/mcdp/libraries/manual.mcdplib/symbols.tex'
    tex = open(symbols).read()
    
    lines = tex.split('\n')
    lines = ['$%s$' % l for l in filter(lambda x: len(x.strip())>0, lines)]
    tex = "\n".join(lines)
    frag = '<div class="mathjax-symbols">%s</div>\n' % tex
    frag = tex
    return frag

def protect_my_envs(s):
    # we don't want MathJax to look inside these
    elements = ['mcdp-value', 'mcdp-poset', 'pre', 'render', 'pos', 'val']
    delimiters = []
    for e in elements:
        delimiters.append(('<%s'%e,'</%s>'%e))
        
    subs = {}
    for d1, d2 in delimiters:
        from mcdp_web.renderdoc.latex_preprocess import extract_delimited
        s = extract_delimited(s, d1, d2, subs, 'MYENVS')
        
    for k, v in list(subs.items()):
        # replace back if k is in a line that is a comment
        # or there is an odd numbers of \n~~~
        if is_inside_markdown_quoted_block(s, s.index(k)):
            s = s.replace(k, v)
            del subs[k]

    return s, subs



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

# UNDERSCORE_IN_FORMULA = 'UNDERSCOREINFORMULA'
# STAR_IN_FORMULA = 'STARINFORMULA'
# 
# def replace_underscore_etc_in_formulas(l):
#     """ Replace the special characters in the formulas """
#     def inside(sf):
#         sf = sf.replace('_', UNDERSCORE_IN_FORMULA)
#         sf = sf.replace('*', STAR_IN_FORMULA)
#         sf = sf.replace('\\', '\\\\')
#         return sf
#     def outside(sf):
#         return sf
#     l = replace_inside_delims(l, '$', inside=inside, outside=outside)
#     return l
    
# def replace_underscore_etc_in_formulas_undo(s):
#     s = s.replace(UNDERSCORE_IN_FORMULA, '_')
#     s = s.replace(STAR_IN_FORMULA, '*')
#     return s

