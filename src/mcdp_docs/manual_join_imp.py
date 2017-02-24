#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys

from bs4 import BeautifulSoup
from bs4.element import Comment, Tag, NavigableString

from contracts import contract
from mcdp import logger
from mcdp_docs.manual_constants import MCDPManualConstants
from mcdp_docs.read_bibtex import get_bibliography
from mcdp_web.renderdoc.highlight import add_class


def get_manual_css_frag():
    """ Returns fragment of doc with CSS, either inline or linked,
        depending on MCDPConstants.manual_link_css_instead_of_including. """
    from mcdp import MCDPConstants 
    
    link_css = MCDPConstants.manual_link_css_instead_of_including
    
    frag = Tag(name='fragment-css')
    if link_css: 
        link = Tag(name='link')
        link['rel'] = 'stylesheet'
        link['type'] = 'text/css'
        link['href'] = 'VERSIONCSS'
        frag.append(link) 
        
        return frag
    else:
        assert False
            
@contract(files_contents='list( tuple( tuple(str,str), str) )', returns='str')
def manual_join(files_contents, bibfile):
    from mcdp_web.renderdoc.main import replace_macros
    from mcdp_utils_xml import bs
    
    fn = MCDPManualConstants.main_template
    if not os.path.exists(fn):
        raise ValueError('Could not find template %s' % fn )
    template = open(fn).read()
    template = replace_macros(template)
    
    # cannot use bs because entire document
    template_soup = BeautifulSoup(template, 'lxml', from_encoding='utf-8')
    d = template_soup 
    assert d.html is not None
    assert '<html' in  str(d)
    head = d.find('head')
    assert head is not None
    for x in get_manual_css_frag().contents:
        head.append(x.__copy__())

    body = d.find('body')
    for (_libname, docname), data in files_contents:
        logger.debug('docname %r -> %s KB' % (docname, len(data)/1024))
        from mcdp_web.renderdoc.latex_preprocess import assert_not_inside
        assert_not_inside(data, 'DOCTYPE')
        frag = bs(data) 
        body.append(NavigableString('\n\n'))
        body.append(Comment('Beginning of document dump of %r' % docname))
        body.append(NavigableString('\n\n'))
        for x in frag.contents:
            x2 = x.__copy__() # not clone, not extract
            body.append(x2) 
        body.append(NavigableString('\n\n'))
        body.append(Comment('End of document dump of %r' % docname))
        body.append(NavigableString('\n\n'))

    logger.info('adding toc')
    toc = generate_doc(body)
    toc_ul = bs(toc).ul
    toc_ul.extract()
    assert toc_ul.name == 'ul'
    toc_ul['class'] = 'toc'
    toc_ul['id'] = 'main_toc'
    
    toc_selector = 'div#toc'
    tocs = list(d.select(toc_selector))
    if not tocs:
        msg = 'Cannot find any element of type %r to put TOC inside.' % toc_selector
        logger.warning(msg)
    else:
        toc_place = tocs[0]
        toc_place.replaceWith(toc_ul)


    logger.info('external bib')
    bibliography_entries = get_bibliography(bibfile)
    bibliography_entries['id'] = 'bibliography_entries'
    body.append(bibliography_entries)
    bibhere = d.find('div', id='put-bibliography-here')
    do_bib(d, bibhere)

    logger.info('reorganizing contents in <sections>')    
    body2 = reorganize_contents(d.find('body'))
    body.replace_with(body2)
    
    logger.info('checking errors')
    check_various_errors(d)

    from mcdp_docs.check_missing_links import check_if_any_href_is_invalid
    logger.info('checking hrefs')
    check_if_any_href_is_invalid(d) 
    
    warn_for_duplicated_ids(d)
    logger.info('converting to string')
    res = str(d) # do not use to_html_stripping_fragment - this is a complete doc
    logger.info('replacing macros')
    res = replace_macros(res)
    logger.info('done - %d bytes' % len(res))
    return res

def do_bib(soup, bibhere):
    """ find used bibliography entries put them there """
    used = set()
    unused = set()
    for a in soup.find_all('a'):
        href = a.attrs.get('href', '')
        if href.startswith('#bib:'):
            used.add(href[1:]) # no "#"
    print('I found %d references, to these: %s' % (len(used), used))
    
    if bibhere is None:
        logger.error('Could not find #put-bibliography-here in document.')
    else:
        cites = list(soup.find_all('cite'))
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
    
def warn_for_duplicated_ids(soup):
    from collections import defaultdict
    
    counts = defaultdict(lambda: [])
    for e in soup.select('[id]'):
        ID = e['id']
        counts[ID].append(e)
        
    problematic = []
    for ID, elements in counts.items():
        n = len(elements)
        if n == 1:
            continue
        
        ignore_if_contains = ['MathJax', 'MJ', 'edge', 'mjx-eqn',]
        if any(_ in ID for _ in ignore_if_contains):
            continue
        
        inside_svg = False
        for e in elements:
            for _ in e.parents:
                if _.name =='svg':
                    inside_svg = True
                    break
        if inside_svg:
            continue  
        
        #msg = ('ID %15s: found %s - numbering will be screwed up' % (ID, n))
        #logger.error(msg)
        problematic.append(ID)
        
        for e in elements:
            t = Tag(name='span')
            t['class'] = 'duplicated-id'
            t.string = 'Error: warn_for_duplicated_ids:  There are %d tags with ID %s' % (n, ID)  
            #e.insert_before(t)
            add_class(e, 'errored')
            
        for i, e in enumerate(elements[1:]):
            e['id'] = e['id'] + '-duplicate-%d' % (i + 1)
            #print('changing ID to %r' % e['id'])
    if problematic:
        logger.error('The following IDs were duplicated: %s' %  ", ".join(problematic))
        logger.error('I renamed some of them; references and numbering are screwed up')
    
        
def reorganize_contents(body0):
    """ reorganizes contents 
    
        h1
        h2
        h1
        
        section
            h1
            h2
        section 
            h1
        
    """ 

    def make_sections(body, is_marker, preserve = lambda _: False, element_name='section'):
        sections = []
        current_section = Tag(name=element_name)
        current_section['id'] = 'before-any-match-of-%s' % is_marker.__name__
        sections.append(current_section)
        for x in body.contents:
            if is_marker(x):
                #print('starting %s' % str(x))
                if len(list(current_section.contents)) > 0:
                    sections.append(current_section)
                current_section = Tag(name=element_name)
                current_section['id'] = x.attrs.get('id', 'unnamed-h1') + ':' + element_name
                current_section['class'] = x.attrs.get('class', '')
                #print('%s/section %s %s' % (is_marker.__name__, x.attrs.get('id','unnamed'), current_section['id']))
                current_section.append(x.__copy__())
            elif preserve(x):
                sections.append(current_section)
                #current_section['id'] = x.attrs.get('id', 'unnamed-h1') + ':' + element_name
                #print('%s/preserve %s' % (preserve.__name__, current_section['id']))
                sections.append(x.__copy__())
                current_section = Tag(name=element_name)
            else:
                current_section.append(x.__copy__())
        sections.append(current_section)     # XXX
        new_body = Tag(name=body.name)
#         if len(sections) < 3:
#             msg = 'Only %d sections found (%s).' % (len(sections), is_marker.__name__)
#             raise ValueError(msg)
        
        logger.info('make_sections: %s found using marker %s' % (len(sections), is_marker.__name__))
        for i, s in enumerate(sections):
            new_body.append('\n')
            new_body.append(Comment('Start of %s section %d/%d' % (is_marker.__name__, i, len(sections))))
            new_body.append('\n')
            new_body.append(s)
            new_body.append('\n')
            new_body.append(Comment('End of %s section %d/%d'% (is_marker.__name__, i, len(sections))))
            new_body.append('\n')
        return new_body
    
    def is_section_marker(x):
        return isinstance(x, Tag) and x.name == 'h2'

    def is_chapter_marker(x):
        return isinstance(x, Tag) and x.name == 'h1' and (not 'part' in x.attrs.get('id',''))
    
    def is_part_marker(x):
        return isinstance(x, Tag) and x.name == 'h1' and 'part' in x.attrs.get('id','')

    body = make_sections(body0, is_section_marker, is_chapter_marker)
    body = make_sections(body, is_chapter_marker, is_part_marker)
    body = make_sections(body, is_part_marker)
    
    def is_h2(x):
        return isinstance(x, Tag) and x.name == 'h2'
     
    body = make_sections(body, is_h2)
            
    return body
    
    
    


def check_various_errors(d):
    error_names = ['DPSemanticError', 'DPSyntaxError']
    selector = ", ".join('.'+_ for _ in error_names)
    errors = list(d.find_all(selector))
    if errors:
        msg = 'I found %d errors in processing.' % len(errors)
        logger.error(msg)
        for e in errors:
            logger.error(e.contents)
            
    fragments = list(d.find_all('fragment'))
    if fragments:
        msg = 'There are %d spurious elements "fragment".' % len(fragments)
        logger.error(msg)
        
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
                    #logger.error(msg)
                    return 'extraheading%s' % i
                    #raise ValueError(msg)
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

    headers = list(soup.findAll(['h1', 'h2', 'h3', 'h4']))
    #print('iterating headers')
    formatter="html"
    formatter = headers[0]._formatter_for_name(formatter)
    for header in headers:
        if header.has_attr('notoc'):
            continue
        ID = header.get('id', None)
        prefix = None if (ID is None or not ':' in ID) else ID[:ID.index(':')] 
        
        allowed_prefixes = {
            'h1': ['sec', 'app', 'part'],
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
        using =  using[:35]
        m = 'header %s %s   %-50s    %s  ' % (' '*2*depth,  header.name, header['id'],  using)
        m = m + ' ' * (120-len(m))
        print(m)
        item = Item(header, depth, using, header['id'], [])
        
        while(stack[-1].depth >= depth):
            stack.pop()
        stack[-1].items.append(item)
        stack.append(item)
        header_id += 1
 
    root = stack[0]

    print('numbering items')
    root.number_items(prefix='', level=0)

    from mcdp_utils_xml import bs

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
            item.tag.insert_after(ul) # XXX: uses <fragment>
            
    print('toc done iterating')
    return root.__str__(root=True)



#     
#     for tag in main_body.select("a"):
#         href = tag['href']
#         # debug(href)
#         # http://127.0.0.1:8080/libraries/tour1/types.html
#         if href.endswith('html'):
#             page = href.split('/')[-1]
#             new_ref = '#%s' % page
#             tag['href'] = new_ref
