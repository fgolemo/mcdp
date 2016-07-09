from contracts import contract

@contract(returns=str)
def render_markdown(s):
    """ Returns an HTML string encoded in UTF-8"""
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
    u = s.decode('utf-8')
    html = markdown.markdown(u, extensions)
    html = html.encode('utf-8')
    return html


