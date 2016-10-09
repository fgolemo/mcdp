#!/usr/bin/env python
import sys

from bs4 import BeautifulSoup

from contracts import contract
from mcdp_report.html import get_language_css, get_markdown_css


manual_css = """

@page {
    margin: 0.5cm;
}

h1 { color: black; }
h2 { color: blue; }
h3 { color: magenta; }

h1 { page-break-before: always; text-align: center;}
h1#booktitle  { page-break-before: avoid; }
h2 { }


.toc a { text-decoration: none; }


/* Good for safari */
pre {
     box-shadow: none;
}

.ndp_graph_expand,
.ndp_graph_enclosed,
.ndp_graph_normal,
.ndp_graph_templatized,
.ndp_graph_templatized_labeled,
.template_graph_enclosed {
    max-width: 50em;
}
"""

@contract(files_contents='list( tuple( tuple(str,str), str) )', returns='str')
def manual_join(files_contents):

    template = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <title>PyMCDP manual</title>
        <meta charset="utf-8">
        <style type='text/css'>CSS</style>

        <script src='https://cdn.mathjax.org/mathjax/latest/MathJax.js?config=TeX-AMS-MML_HTMLorMML'></script>

        <script type="text/x-mathjax-config">
            MathJax.Hub.Config({
              tex2jax: {inlineMath: [['$','$']]}
            });
        </script>

    </head>
    <body>
    <h1 id='booktitle'>The PyMCDP user manual</h1>
    <div id='toc'/>
    <div id='body'/>
    </body>
    </html>
    """

    # css = urllib2.urlopen('http://127.0.0.1:8080/static/css/mcdp_language_highlight.css').read()
    # other = urllib2.urlopen('http://127.0.0.1:8080/static/css/markdown.css').read()
#     extra = open('manual.css').read()
    markdown_css = get_markdown_css()
    mcdp_css = get_language_css()
    template = template.replace('CSS', mcdp_css + '\n' + manual_css + '\n' + markdown_css)
    d = BeautifulSoup(template, 'lxml')
    main_body = BeautifulSoup("", 'lxml')

    for (_libname, docname), data in files_contents:
        doc = BeautifulSoup(data, 'lxml', from_encoding='utf-8')

        body = doc.body
        body.name = 'div'
        body['id'] = docname
        main_body.append(body)

    for tag in main_body.select("a"):
        href = tag['href']
        # debug(href)
        # http://127.0.0.1:8080/libraries/tour1/types.html
        if href.endswith('html'):
            page = href.split('/')[-1]
            new_ref = '#%s' % page
            tag['href'] = new_ref

    toc = generate_doc(main_body)
    toc = BeautifulSoup(toc, 'lxml')
    toc['class'] = 'toc'
    toc['id'] = 'toc'
    toc_place = d.select('div#toc')[0]
    body_place = d.select('div#body')[0]
    toc_place.replaceWith(toc)

    body_place.replaceWith(main_body)

    return str(d)

def debug(s):
    sys.stderr.write(str(s) + ' \n')

def generate_doc(soup):

    header_id = 1

    class Item():
        def __init__(self, tag, depth, name, _id, items):
            self.tag = tag
            self.name = name
            self.depth = depth
            self.id = _id
            self.items = items
#             for i in items:
#                 assert isinstance(items)

            self.number = None

        def number_items(self, prefix, level):
            self.number = prefix

            if self.tag:
                self.tag.string = prefix + ' - ' + self.tag.string

            def get_number(i, level):
                if level == 0 or level == 1:
                    headings = ['%d' % (j + 1) for j in range(20)]
                elif level == 2:
                    headings = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L',
                        'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'Z']

                else:
                    return ''

                if i >= len(headings):
                    msg = 'i = %d level %s headings = %s' % (i, level, headings)
                    raise ValueError(msg)
                return headings[i]

            if prefix:
                prefix = prefix + '.'
            for i, item in enumerate(self.items):
                item_prefix = prefix + get_number(i, level)
                item.number_items(item_prefix, level + 1)




        def __str__(self, root=False):
            s = ''
            if not root:
                s += '<a href="#%s">%s - %s</a>' % (self.id, self.number, self.name)
            if self.items:
                s += '<ul>'
                for item in self.items:
                    s += '<li>%s</li>' % item
                s += '</ul>'
            return s

    stack = [ Item(None, 0, 'root', 'root', []) ]

    for header in soup.findAll(['h1', 'h2', 'h3']):
        header['id'] = header_id

        depth = int(header.name[1])

        # previous_depth = stack[-1].depth

        item = Item(header, depth, header.string, header['id'], [])

        while(stack[-1].depth >= depth):
            stack.pop()
        stack[-1].items.append(item)
        stack.append(item)
        header_id += 1


    root = stack[0]

    root.number_items(prefix='', level=0)

    for item in root.items:
        s = item.__str__(root=True)
        stoc = BeautifulSoup(s, 'lxml')
        stoc['class'] = 'toc'
        item.tag.insert_after(stoc)


    return root.__str__(root=True)

