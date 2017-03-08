# -*- coding: utf-8 -*-
from contracts import contract
from contracts.utils import raise_desc


@contract(s=bytes, returns=bytes)
def render_markdown(s): # pragma: no cover
    """ Returns an HTML string encoded in UTF-8"""
    if isinstance(s, unicode):
        msg = 'I expect utf-8 encoded bytes.'
        raise_desc(TypeError, msg, s=s.__repr__())

    import markdown  # @UnresolvedImport
    import logging
    logging.getLogger("MARKDOWN").setLevel(logging.CRITICAL)

    extensions = [
        'markdown.extensions.smarty',
        'markdown.extensions.toc',
        'markdown.extensions.attr_list',
        'markdown.extensions.extra', # need for markdown=1
        'markdown.extensions.fenced_code',
        'markdown.extensions.admonition',
        'markdown.extensions.tables',
    ]
    

    # markdown takes and returns unicode
    u = unicode(s, 'utf-8')
    html = markdown.markdown(u, extensions)
    html = html.encode('utf-8')
    return html


