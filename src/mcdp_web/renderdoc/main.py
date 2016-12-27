# -*- coding: utf-8 -*-
from contracts import contract
from contracts.utils import raise_desc, indent
from mcdp_library import MCDPLibrary
from mcdp_web.renderdoc.abbrevs import other_abbrevs
from mcdp_web.renderdoc.highlight import fix_subfig_references
from mcdp_web.renderdoc.latex_preprocess import extract_maths, extract_tabular,\
    assert_not_inside
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
import itertools
from mcdp_web.renderdoc.lessc import preprocess_lessc
from mcdp_web.renderdoc.xmlutils import to_html_stripping_fragment, bs
import mocdp
import datetime


__all__ = ['render_document']

@contract(returns='str', s=str, library=MCDPLibrary, raise_errors=bool)
def render_complete(library, s, raise_errors, realpath, generate_pdf=False,
                    check_refs=False):
    """
        Transforms markdown into html and then renders the mcdp snippets inside.
        
        s: a markdown string with embedded html snippets
        
        Returns an HTML string; not a complete document.
    """
    if isinstance(s, unicode):
        msg = 'I expect a str encoded with utf-8, not unicode.'
        raise_desc(TypeError, msg, s=s)

    s = replace_macros(s)
    # need to do this before do_preliminary_checks_and_fixes 
    # because of & char
    s, tabulars = extract_tabular(s)
   
    s = do_preliminary_checks_and_fixes(s)
    # put back tabular, because extract_maths needs to grab them
    for k,v in tabulars.items():
        assert k in s
        s = s.replace(k, v)
        
    s = s.replace('%\n', '&nbsp;')
    # copy all math content,
    #  between $$ and $$
    #  between various limiters etc.
    # returns a dict(string, substitution)
    s, maths = extract_maths(s) 
#     print('maths = %s' % maths)
    for k, v in maths.items():
        if v[0] == '$' and v[1] != '$$':
            if '\n\n' in v:
                msg = 'Suspicious math fragment %r = %r' % (k, v)
                logger.error(maths)
                logger.error(msg)
                raise ValueError(msg)
    
    # fixes for LaTeX
    s = latex_preprocessing(s)
    assert not '\\par' in s
    assert not '\\vspace' in s
    assert not 'begin{tabular}' in s
    
    s = '<div style="display:none">Because of mathjax bug</div>\n\n\n' + s

    # cannot parse html before markdown, because md will take
    # invalid html, (in particular '$   ciao <ciao>' and make it work)
    
    s = s.replace('*}', '\*}')
#     def markdown_fixes(l):
#         l = replace_backticks_except_in_backticks_expression(l)
#         l = replace_underscore_etc_in_formulas(l)
#         return l

    s = other_abbrevs(s)
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
    
    
    # need to process tabular before mathjax 
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
    from mcdp_docs.check_missing_links import check_if_any_href_is_invalid
    
    if check_refs:
        d = bs(s)
        check_if_any_href_is_invalid(d)
        s = to_html_stripping_fragment(d)

    check_html_fragment(s) 
    
    s = preprocess_lessc(s)
    
    s = fix_validation_problems(s)
    return s

def replace_macros(s):
    macros = {}
    macros['PYMCDP_VERSION'] = mocdp.__version__
    # 'July 23, 2010'
    macros['PYMCDP_COMPILE_DATE'] = datetime.date.today().strftime("%B %d, %Y") 
    macros['PYMCDP_COMPILE_TIME'] = datetime.datetime.now().strftime("%I:%M%p")
    
    for k, v in macros.items():
        s = s.replace(k, v)
        
    assert_not_inside(s, 'PYMCDP_')
    return s

def fix_validation_problems(s):
    """ Fixes things that make the document not validate. """
    soup = bs(s)
    
    # remove the attributes span.c and span.ce used in ast_to_html
    for e in soup.select('span[c]'):
        del e.attrs['c']
    for e in soup.select('span[ce]'):
        del e.attrs['ce']

    also_remove = ['figure-id', 'figure-class', 'figure-caption']
    also_remove.extend('make-col%d' % _ for _ in range(1, 12))
    
    for a in also_remove:
        for e in soup.select('[%s]' % a):
            del e.attrs[a]
        
    # add missing type for <style>
#     for e in soup.select('style:not([type])'):
    for e in soup.select('style'):
        if not 'type' in e.attrs:
            e.attrs['type'] = 'text/css'

    for e in soup.select('span.MathJax_SVG'):
        style = e.attrs['style']
        style = style.replace('display: inline-block;' ,'/* decided-to-ignore-inline-block: 0;*/')
        e.attrs['style'] = style
        
    # remove useless <defs id="MathJax_SVG_glyphs"></defs>
#     for e in list(soup.select('defs')):
#         if e.attrs.get('id',None) == "MathJax_SVG_glyphs" and not e.string:
#             e.extract()
        
#     for e in soup.select('svg'):
#         xmlns = "http://www.w3.org/2000/svg"
#         if not 'xmlns' in e.attrs:
#             e.attrs['xmlns'] = xmlns
            
    return to_html_stripping_fragment(soup)

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
    elements = ['mcdp-value', 'mcdp-poset', 'pre', 'render', 
                'poset', 'pos',
                'value', 'val']
    # "poset" must be before "pos"
    # "value" must be before "val"
    
    for e1, e2 in itertools.product(elements, elements):
        if e1 == e2: continue
        if e1.startswith(e2):
            assert elements.index(e1) < elements.index(e2)
            
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

