
def render_markdown(s):
    """ Returns an HTML string """
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
    html = markdown.markdown(s, extensions)
    return html


