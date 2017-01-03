# -*- coding: utf-8 -*-
import itertools
from string import Template

from contracts import contract
from contracts.interface import location, Where
from contracts.utils import raise_desc, indent
from mcdp_docs.manual_constants import MCDPManualConstants
from mcdp_library import MCDPLibrary
from mcdp_report.gg_utils import embed_images_from_library2
from mocdp import logger
from mocdp.exceptions import DPInternalError, DPSyntaxError

from .abbrevs import other_abbrevs
from .highlight import fix_subfig_references, html_interpret,  mark_console_pres,\
    escape_for_mathjax, make_figure_from_figureid_attr
from .xmlutils import check_html_fragment, to_html_stripping_fragment, bs
from mcdp_web.renderdoc.xmlutils import describe_tag


__all__ = [
    'render_complete',
]

@contract(returns='str', s=str, library=MCDPLibrary, raise_errors=bool)
def render_complete(library, s, raise_errors, realpath, generate_pdf=False,
                    check_refs=False):
    """
        Transforms markdown into html and then renders the mcdp snippets inside.
        
        s: a markdown string with embedded html snippets
        
        Returns an HTML string; not a complete document.
    """
    from .latex_preprocess import extract_maths, extract_tabular
    from .latex_preprocess import latex_preprocessing
    from .lessc import preprocess_lessc
    from .macro_col2 import col_macros, col_macros_prepare_before_markdown
    from .markd import render_markdown
    from .preliminary_checks import do_preliminary_checks_and_fixes
    from .prerender_math import prerender_mathjax
    from .latex_preprocess import replace_equations

    if isinstance(s, unicode):
        msg = 'I expect a str encoded with utf-8, not unicode.'
        raise_desc(TypeError, msg, s=s)

    
    # need to do this before do_preliminary_checks_and_fixes 
    # because of & char
    s, tabulars = extract_tabular(s)
   
    s = do_preliminary_checks_and_fixes(s)
    # put back tabular, because extract_maths needs to grab them
    for k,v in tabulars.items():
        assert k in s
        s = s.replace(k, v)
        
    
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
    
    s = '<div style="display:none">Because of mathjax bug</div>\n\n\n' + s

    # cannot parse html before markdown, because md will take
    # invalid html, (in particular '$   ciao <ciao>' and make it work)
    
    s = s.replace('*}', '\*}') 

    s = other_abbrevs(s)
    s, mcdpenvs = protect_my_envs(s) 
#     print('mcdpenvs = %s' % maths)

    
    s = col_macros_prepare_before_markdown(s)
    
#     print(indent(s, 'before markdown | '))
    s = render_markdown(s)
#     print(indent(s, 'after  markdown | '))
    
    for k,v in maths.items():
        if not k in s:
            msg = 'Cannot find %r (= %r)' % (k, v)
            raise_desc(DPInternalError, msg, s=s)
        def preprocess_equations(x):
            # this gets mathjax confused
            x = x.replace('>', '\\gt{}') # need brace; think a<b -> a\lt{}b
            x = x.replace('<', '\\lt{}')
#             print('replaced equation %r by %r ' % (x0, x))
            return x
            
        v = preprocess_equations(v)
        s = s.replace(k, v)

    s = replace_equations(s)        
    s = s.replace('\\*}', '*}')
    
    
    # need to process tabular before mathjax 
    s = escape_for_mathjax(s)

#     print(indent(s, 'before prerender_mathjax | '))
    # mathjax must be after markdown because of code blocks using "$"
    
    s = prerender_mathjax(s)
#     print(indent(s, 'after prerender_mathjax | '))
    for k,v in mcdpenvs.items():
        # there is this case:
        # ~~~
        # <pre> </pre>
        # ~~~
        s = s.replace(k, v)

    

    s = s.replace('<p>DRAFT</p>', '<div class="draft">')
    
    s = s.replace('<p>/DRAFT</p>', '</div>')
    
    s = mark_console_pres(s)
    s = make_figure_from_figureid_attr(s)
    
    s = col_macros(s)
    
#     print(indent(s, 'after  col_macros | '))
    s = fix_subfig_references(s)
    check_html_fragment(s)
    
#     print(indent(s, 'before  html_interpret | '))
    library = get_library_from_document(s=s, default_library=library)
    s = html_interpret(library, s, generate_pdf=generate_pdf,
                           raise_errors=raise_errors, realpath=realpath)

    check_html_fragment(s)
    
    raise_missing_image_errors = False
    
    soup = bs(s)
    
    embed_images_from_library2(soup=soup, library=library, 
                              raise_errors=raise_missing_image_errors)
        
    if check_refs:    
        from mcdp_docs.check_missing_links import check_if_any_href_is_invalid
        check_if_any_href_is_invalid(soup=soup)
        
    s = to_html_stripping_fragment(soup)

    check_html_fragment(s) 
    
    s = preprocess_lessc(s)
    
    s = fix_validation_problems(s)
    return s

def get_document_properties(s):
    """ Reads a document's <meta> tags into a dict """
    soup = bs(s)
    metas = list(soup.select('meta'))
    FK, FV = 'name', 'content'
    properties = {}
    for e in metas:
        if not FK in e.attrs or not FV in e.attrs:
            msg = 'Expected "%s" and "%s" attribute for meta tag.' % (FK, FV)
            raise_desc(ValueError, msg, tag=describe_tag(e))
            
        properties[e[FK]] = e[FV]
    return properties
    
def get_library_from_document(s, default_library):
    """
        Reads a tag like this:
        
            <meta name="mcdp-library" content='am'/>

    """ 
    properties = get_document_properties(s)
    print('properties: %s' % properties)
        
    KEY_MCDP_LIBRARY = 'mcdp-library'
    if KEY_MCDP_LIBRARY in properties:
        use = properties[KEY_MCDP_LIBRARY]
        print('using library %r ' % use)
        library = default_library.load_library(use)
        return library
        
    return default_library


def replace_macros(s):    
    macros = MCDPManualConstants.macros
    class MyTemplate(Template):
        delimiter = '@@'
        def _invalid(self, mo):
            i = mo.start('invalid')
            lines = self.template[:i].splitlines(True)
            if not lines:
                colno = 1
                lineno = 1
            else:
                colno = i - len(''.join(lines[:-1]))
                lineno = len(lines)
                
            char = location(lineno-1, colno-1, s)
            w = Where(s, char)
            raise DPSyntaxError('Invalid placeholder', where=w)

    t = MyTemplate(s)
    try:
        s2 = t.substitute(macros)
    except KeyError as e:
        key = str(e).replace("'","")
        search_for = MyTemplate.delimiter + key
        char = s.index(search_for)
        w = Where(s, char)
        msg = 'Key %r not found - maybe use braces?' % key
        raise DPSyntaxError(msg, where=w)
    return s2 

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
#     frag = '<div class="mathjax-symbols">%s</div>\n' % tex
    frag = tex
    return frag

def protect_my_envs(s):
    from .markdown_transform import is_inside_markdown_quoted_block

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
        if k in s: # it might be recursively inside something
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

# def replace_backticks_except_in_backticks_expression(l):
#     def inside(sf):
#         sf = sf.replace('`', '&#96;')
#         return sf
#     def outside(sf):
#         return sf
#     return replace_inside_delims(l, '$', inside=inside, outside=outside)

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

