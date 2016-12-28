#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys

from bs4.element import Comment, Tag

from contracts import contract
from mcdp_docs.manual_constants import MCDPManualConstants
from mcdp_docs.read_bibtex import get_bibliography
from mcdp_web.renderdoc.highlight import add_class
from mocdp import logger


def get_manual_css_frag():
    """ Returns fragment of doc with CSS, either inline or linked,
        depending on MCDPConstants.manual_link_css_instead_of_including. """
    from mocdp import MCDPConstants
    from mcdp_report.html import \
    get_manual_print_css_filename, get_manual_screen_css_filename,\
    get_manual_generic_css_filename, get_markdown_css_filename,\
    get_language_css_filename, get_reset_css_filename

    css_files = [
        get_reset_css_filename(),
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
    fn = MCDPManualConstants.main_template
    if not os.path.exists(fn):
        raise ValueError('Could not find %s' % fn )
    template = open(fn).read()
    
    from mcdp_web.renderdoc.main import replace_macros
    template = replace_macros(template)
    
    frag = get_manual_css_frag()
    template = template.replace('CSS', frag)
    template = template.replace('TITLE', 'Practical Tools for Co-Design')
    
    
    # title page
    (_libname, docname), first_data = files_contents.pop(0)
    assert 'first' in docname
    
    from mcdp_web.renderdoc.xmlutils import bs
    first_contents = bs(first_data)
    first_contents.name = 'div'
    
    first_contents['class'] = 'doc'
    first_contents['docname'] = docname
    template = template.replace('FIRSTPAGE', str(first_contents))
    
    d = bs(template)
    
    # empty document
    main_body = Tag(name='div', attrs={'id':'main_body'})

    for (_libname, docname), data in files_contents:
        print('docname %r -> %s KB' % (docname, len(data)/1024))
        from mcdp_web.renderdoc.latex_preprocess import assert_not_inside
        assert_not_inside(data, 'DOCTYPE')
        frag = bs(data)
#         frag.name = 'div' # from fragment
#         frag.attrs['title'] = "This was the contents of %r, now a DIV." % docname
#         frag['id'] = docname
        main_body.append('\n')
        main_body.append(Comment('Beginning of body of %r' % docname))
        main_body.append('\n')
        if True:
            for x in frag.contents:
                x2 = x.__copy__() # not clone, not extract
                main_body.append(x2)
        else: 
            main_body.append(frag)
        main_body.append('\n')
        main_body.append(Comment('End of body of %r' % docname))

    
    for tag in main_body.select("a"):
        href = tag['href']
        # debug(href)
        # http://127.0.0.1:8080/libraries/tour1/types.html
        if href.endswith('html'):
            page = href.split('/')[-1]
            new_ref = '#%s' % page
            tag['href'] = new_ref

    print('adding toc')
    toc = generate_doc(main_body)
    toc_ul = bs(toc).ul
    toc_ul.extract()
    assert toc_ul.name == 'ul'
    toc_ul['class'] = 'toc'
    toc_ul['id'] = 'main_toc'
    toc_place = d.select('div#toc')[0]
    body_place = d.select('div#body')[0]
    
    #print('toc element: %s' % str(toc))
    toc_place.replaceWith(toc_ul)

    print('replacing body_place with main_body')
    body_place.replaceWith(main_body)
    main_body.insert_after(Comment('end of main_body'))

    print('external bib')
    bibliography_entries = get_bibliography()
    bibliography_entries['id'] = 'bibliography_entries'
    d.find(id='bibliography_entries').replace_with(bibliography_entries)
    
    
    # find used bibliography entries
    used = set()
    unused = set()
    for a in d.find_all('a'):
        href = a.attrs.get('href', '')
        if href.startswith('#bib:'):
            used.add(href[1:]) # no "#"
    print('I found %d references, to these: %s' % (len(used), used))
    bibhere = d.find('div', id='put-bibliography-here')
    if bibhere is None:
        logger.error('Could not find #put-bibliography-here in document.')
    else:
        cites = list(d.find_all('cite'))
        # TODO: sort
        for c in cites:
            ID = c.attrs.get('id', None)
            if ID in used:
                # remove it from parent
                c.extract()
                # add to bibliography
                bibhere.append(c)
                add_class(c, 'used')
            else:
                unused.add(ID)
                add_class(c, 'unused')
    print('I found %d unused bibs.' % (len(unused)))
    print('checking errors')
    check_various_errors(d)
    
    from mcdp_docs.check_missing_links import check_if_any_href_is_invalid
    print('checking hrefs')
    check_if_any_href_is_invalid(d) 
    print('converting to string')
    res = str(d) # do not use to_html_stripping_fragment - this is a complete doc
    print('done - %d bytes' % len(res))
    return res

    


def check_various_errors(d):
    error_names = ['DPSemanticError', 'DPSyntaxError']
    selector = ", ".join('.'+_ for _ in error_names)
    errors = list(d.find_all(selector))
    if errors:
        msg = 'I found %d errors in processing.' % len(errors)
        logger.error(msg)
        for e in errors:
            logger.error(e.contents)
            
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
                
                if False:
                    span = Tag(name='span')
                    span['class'] = 'toc_number'
                    span.string = prefix + ' – '
                    self.tag.insert(0, span)
                else:
                    msg = 'number_items: By my count, this should be %r.' % prefix
                    self.tag.insert_after(Comment(msg))
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
                s += (u"""<a class="toc_link" href="#%s">
                            <span class="toc_number">%s –</span> 
                            <span class="toc_name">%s</span></a>""" % 
                            (self.id, self.number, self.name))
            if self.items:
                s += '<ul>'
                for item in self.items:
                    s += '<li>%s</li>' % item
                s += '</ul>'
            return s

    stack = [ Item(None, 0, 'root', 'root', []) ]

    print('Finding headers')
    headers = list(soup.findAll(['h1', 'h2', 'h3', 'h4']))
    print('iterating headers')
    formatter="html"
    formatter = headers[0]._formatter_for_name(formatter)
    for header in headers:
        ID = header.get('id', None)
        prefix = None if (ID is None or not ':' in ID) else ID[:ID.index(':')] 
        
        allowed_prefixes = {
            'h1': ['sec', 'app'],
            'h2': ['sub', 'appsub'],
            'h3': ['subsub', 'appsubsub'],
            'h4': ['par'],
        }[header.name]
        default_prefix = allowed_prefixes[0]
        
        if ID is None: 
            header['id'] = '%s:%s' % (default_prefix, header_id)
        else:
            if prefix is None: 
                #msg = 'Invalid ID %r for tag %r, muststart with %r.' % (cur, header.name, prefix)
                #raise_desc(ValueError, msg, tag=str(header))
                msg = ('Adding prefix %r to current id %r for %s.' % 
                       (default_prefix, ID, header.name))
                #logger.debug(msg)
                header.insert_before(Comment('Warning: ' + msg))
                header['id'] = default_prefix + ':' + ID
            else:
                if prefix not in allowed_prefixes:
                    msg = ('The prefix %r is not allowed for %s (ID=%r)' % 
                           (prefix, header.name, ID))
                    logger.error(msg)
                    header.insert_after(Comment('Error: ' + msg))
                    
        depth = int(header.name[1])

        using = header.decode_contents(formatter=formatter)
        print('header %s %s %s ' % (' '*2*depth, header.name, using))
        item = Item(header, depth, using, header['id'], [])
        
        while(stack[-1].depth >= depth):
            stack.pop()
        stack[-1].items.append(item)
        stack.append(item)
        header_id += 1
 
    root = stack[0]

    print('numbering items')
    root.number_items(prefix='', level=0)

    from mcdp_web.renderdoc.xmlutils import bs

    print('toc iterating')
    # iterate over chapters (below each h1)
    for item in root.items:
        s = item.__str__(root=True)
        stoc = bs(s)
        if stoc.ul is not None: # empty document case
            ul = stoc.ul
            ul.extract() 
            ul['class'] = 'toc chapter_toc'
            # todo: add specific h1
            item.tag.insert_after(ul)
            
    print('toc done iterating')
    return root.__str__(root=True)

