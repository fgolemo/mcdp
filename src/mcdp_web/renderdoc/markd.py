from contracts import contract
from contracts.utils import raise_desc


@contract(s=str, returns=str)
def render_markdown(s):
    """ Returns an HTML string encoded in UTF-8"""
    if isinstance(s, unicode):
        msg = 'I expect a utf-8 string.'
        raise_desc(TypeError, msg, s=s.__repr__())

    import markdown  # @UnresolvedImport

    extensions = [
        'markdown.extensions.smarty',
        'markdown.extensions.toc',
        'markdown.extensions.attr_list',
        # 'markdown.extensions.extra',
        'markdown.extensions.fenced_code',
        'markdown.extensions.admonition',
        'markdown.extensions.tables',
    ]

    # markdown takes and returns unicode
    u = unicode(s, 'utf-8')
    html = markdown.markdown(u, extensions)
    html = html.encode('utf-8')
    return html


