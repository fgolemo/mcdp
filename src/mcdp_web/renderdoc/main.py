from contracts import contract
from mcdp_library.library import MCDPLibrary
from mcdp_web.renderdoc.markd import render_markdown
from mcdp_web.renderdoc.highlight import html_interpret
from contracts.utils import raise_desc


@contract(returns='str', s=str, library=MCDPLibrary, raise_errors=bool)
def render_complete(library, s, raise_errors, realpath):
    """
        Transforms markdown into html and then renders the mcdp snippets inside.
        
        s: a markdown string with embedded html snippets
        
        Returns an HTML string.
    """
    if isinstance(s, unicode):
        msg = 'I expect a utf-8 string.'
        raise_desc(TypeError, msg, s=s)

    html = render_markdown(s)
    html2 = html_interpret(library, html, raise_errors=raise_errors, realpath=realpath)
    return html2
