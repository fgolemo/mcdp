# -*- coding: utf-8 -*-
from contracts import contract
from contracts.utils import raise_desc
from mcdp_library import MCDPLibrary

from .highlight import html_interpret
from .markd import render_markdown
from .prerender_math import prerender_mathjax, PrerenderError
from mcdp_library_tests.tests import timeit_wall
from mcdp_web.renderdoc.highlight import mark_console_pres


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

    # save the '\\' in mathjax before markdown
    s = s.replace('\\\\', 'MATHJAX_BARBAR')

    html = render_markdown(s)
#     print '\nafter render_markdown: %s' % html
    html2 = html_interpret(library, html, generate_pdf=generate_pdf,
                           raise_errors=raise_errors, realpath=realpath)

    from mcdp_report.gg_utils import embed_images_from_library
    html3 = embed_images_from_library(html=html2, library=library)
    
#     print '\nafter embed_images_from_library: %s' % html3
    
    html3 = html3.replace('MATHJAX_BARBAR', '\\\\')
    if '$$' in html3 or '$' in html3:
        try:
            with timeit_wall('prerender_mathjax'):
                html4 = prerender_mathjax(html3)
        except PrerenderError:
            raise
    else:
        html4 = html3
#     print '\nafter prerender_mathjax: %s' % html4

    html5 = mark_console_pres(html4)
    return html5
