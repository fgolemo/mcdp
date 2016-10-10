from contracts import contract
from contracts.utils import raise_desc
from mcdp_library import MCDPLibrary

from .highlight import html_interpret
from .markd import render_markdown


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

    html = render_markdown(s)
    html2 = html_interpret(library, html, generate_pdf=generate_pdf,
                           raise_errors=raise_errors, realpath=realpath)

    from mcdp_report.gg_utils import embed_images_from_library
    html3 = embed_images_from_library(html=html2, library=library)
    return html3
