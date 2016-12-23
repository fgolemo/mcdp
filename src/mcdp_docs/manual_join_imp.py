#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys

from bs4 import BeautifulSoup

from contracts import contract
from contracts.utils import raise_desc
from mocdp import logger
from bs4.element import Comment


def get_manual_css_frag():
    """ Returns fragment of doc with CSS, either inline or linked,
        depending on MCDPConstants.manual_link_css_instead_of_including. """
    from mocdp import MCDPConstants
    from mcdp_report.html import \
    get_manual_print_css_filename, get_manual_screen_css_filename,\
    get_manual_generic_css_filename, get_markdown_css_filename,\
    get_language_css_filename

    css_files = [
        get_language_css_filename(),
        get_markdown_css_filename(),
        get_manual_generic_css_filename(),
        get_manual_screen_css_filename(),
        get_manual_print_css_filename()
    ]
    
    link_css = MCDPConstants.manual_link_css_instead_of_including
    
    if link_css:
        frag = ""
        for fn in css_files:
            url = 'file://%s' % fn
            frag += '\n<link rel="stylesheet" type="text/css" href="%s">\n' % url 
        return frag
    else:
        assert False
            
@contract(files_contents='list( tuple( tuple(str,str), str) )', returns='str')
def manual_join(files_contents):

#         <script src='https://cdn.mathjax.org/mathjax/latest/MathJax.js?config=TeX-AMS-MML_HTMLorMML'></script>
# 
#         <script type="text/x-mathjax-config">
#             MathJax.Hub.Config({
#               tex2jax: {inlineMath: [['$','$']]},
#                 displayMath: [ ['$$','$$'], ["\\[","\\]"] ]
#             });
#         </script>


    template = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <title>TITLE</title>
        <meta charset="utf-8">
        CSS
        </head>
    <body>
    FIRSTPAGE
    <div id='body'/>
    </body>
    </html>
    """ 
    
    frag = get_manual_css_frag()
    template = template.replace('CSS', frag)
    template = template.replace('TITLE', 'Practical Tools for Co-Design')
    
    # title page
    (_libname, docname), first_data = files_contents.pop(0)
    assert docname == 'firstpage'
    
    first_dom = BeautifulSoup(first_data, 'lxml', from_encoding='utf-8')
    first_contents = first_dom.html.body
    first_contents.name = 'div'
    first_contents['class'] = 'doc'
    first_contents['docname'] = docname
    template = template.replace('FIRSTPAGE', str(first_contents))
    
    d = BeautifulSoup(template, 'lxml', from_encoding='utf-8')
    
    # empty document
    main_body = BeautifulSoup("", 'lxml', from_encoding='utf-8')

    for (_libname, docname), data in files_contents:
        doc = BeautifulSoup(data, 'lxml', from_encoding='utf-8')
        body = doc.html.body
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
    toc_ul = BeautifulSoup(toc, 'lxml', from_encoding='utf-8').html.body.ul
    toc_ul['class'] = 'toc'
    toc_ul['id'] = 'main_toc'
    toc_place = d.select('div#toc')[0]
    body_place = d.select('div#body')[0]
    
    #print('toc element: %s' % str(toc))
    toc_place.replaceWith(toc_ul)

    body_place.replaceWith(main_body)

    bibhere = d.find('div', id='put-bibliography-here')
    if bibhere is None:
        logger.error('Could not find #put-bibliography-here in document.')
    else:
        cites = list(d.find_all('cite'))
        # TODO: sort
        for c in cites:
            # remove it from parent
            c.extract()
            # add to bibliography
            bibhere.append(c)

    res = str(d)
    
    from mcdp_docs.check_missing_links import check_if_any_href_is_invalid
    check_if_any_href_is_invalid(res)
    
    
    
    return res

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

            if self.tag is not None:
                # add a span inside the header
                span = soup.new_tag('span')
                span['class'] = 'toc_number'
                span.string = prefix + ' – '
                self.tag.insert(0, span)
                #self.tag.string = prefix + ' - ' + self.tag.string

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
                    logger.error(msg)
                    return 'extraheading%s' % i
                    raise ValueError(msg)
                return headings[i]

            if prefix:
                prefix = prefix + '.'
            for i, item in enumerate(self.items):
                item_prefix = prefix + get_number(i, level)
                item.number_items(item_prefix, level + 1)

        def __str__(self, root=False):
            s = u''
            if not root:
                s += u"""<a class="toc_link" href="#%s">
                            <span class="toc_number">%s –</span> 
                            <span class="toc_name">%s</span></a>""" % (self.id, self.number, self.name)
            if self.items:
                s += '<ul>'
                for item in self.items:
                    s += '<li>%s</li>' % item
                s += '</ul>'
            return s

    stack = [ Item(None, 0, 'root', 'root', []) ]

    for header in list(soup.findAll(['h1', 'h2', 'h3'])):
        
        prefix = {'h1':'sec','h2':'sub','h3':'subsub'}[header.name]
        
        if not header.has_attr('id'):    
            header['id'] = '%s:%s' % (prefix, header_id)
        else:
            cur = header['id']
            if not cur.startswith(prefix+':'):
                #msg = 'Invalid ID %r for tag %r, muststart with %r.' % (cur, header.name, prefix)
                #raise_desc(ValueError, msg, tag=str(header))
                msg = 'Adding prefix %r to current id %r for %s.' % (prefix, cur, header.name)
                header['id'] = prefix + ':' + cur
                logger.debug(msg)
                header.parent.insert(header.parent.index(header), 
                                     Comment('Warning: ' + msg))
        depth = int(header.name[1])

        # previous_depth = stack[-1].depth

        using = header.decode_contents(formatter="html")
#         print("%s or %s using %s" % (str(header), header.string, using))
        item = Item(header, depth, using, header['id'], [])

        while(stack[-1].depth >= depth):
            stack.pop()
        stack[-1].items.append(item)
        stack.append(item)
        header_id += 1


    root = stack[0]

    root.number_items(prefix='', level=0)

    # iterate over chapters (below each h1)
    for item in root.items:
        s = item.__str__(root=True)
        stoc = BeautifulSoup(s, 'lxml', from_encoding='utf-8')
        if stoc.html is not None: # empty document case
            ul = stoc.html.body.ul 
            ul['class'] = 'toc chapter_toc'
            # todo: add specific h1
            item.tag.insert_after(ul)


    return root.__str__(root=True)

