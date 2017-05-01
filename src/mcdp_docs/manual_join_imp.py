#!/usr/bin/env python
# -*- coding: utf-8 -*-
from contracts import contract
from mcdp.logs import logger
from mcdp_utils_xml import add_class
import os
import sys

from bs4 import BeautifulSoup
from bs4.element import Comment, Tag, NavigableString

from .macros import replace_macros
from .manual_constants import MCDPManualConstants
from .read_bibtex import get_bibliography
from .tocs import generate_toc


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
def manual_join(src_dir, files_contents, bibfile, stylesheet, remove=None):
    """
        
        Remove: selector for elements to remove (e.g. ".draft").
        
    """
    from mcdp_utils_xml import bs
    
    fn = os.path.join(src_dir, MCDPManualConstants.main_template)
    if not os.path.exists(fn):
        msg = 'Could not find template %s' % fn 
        raise ValueError(msg)
    
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
        
    if stylesheet is not None:
        link = Tag(name='link')
        link['rel'] = 'stylesheet'
        link['type'] = 'text/css'
        from mcdp_report.html import get_css_filename
        link['href'] = get_css_filename('compiled/%s' % stylesheet)
        head.append(link) 

    body = d.find('body')
    for (_libname, docname), data in files_contents:
        logger.debug('docname %r -> %s KB' % (docname, len(data)/1024))
        from mcdp_docs.latex.latex_preprocess import assert_not_inside
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


    logger.info('external bib')
    if not os.path.exists(bibfile):
        logger.error('Cannot find bib file %s' % bibfile)
    else:
        bibliography_entries = get_bibliography(bibfile)
        bibliography_entries['id'] = 'bibliography_entries'
        body.append(bibliography_entries)
        bibhere = d.find('div', id='put-bibliography-here')
        do_bib(d, bibhere)

    logger.info('reorganizing contents in <sections>')    
    body2 = reorganize_contents(d.find('body'))
    body.replace_with(body2)
    
    ### Removing
    if remove is not None:
        nremoved = 0
        for x in body2.select(remove):
            nremoved += 1
            x.extract()
        logger.info('Removed %d elements of selector %r' % (nremoved, remove))
    
    ###
    logger.info('adding toc')
    toc = generate_toc(body2)
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
    
    logger.info('checking errors')
    check_various_errors(d)

    from mcdp_docs.check_missing_links import check_if_any_href_is_invalid
    logger.info('checking hrefs')
    check_if_any_href_is_invalid(d) 
    
    warn_for_duplicated_ids(d)
    logger.info('converting to string')
    res = str(d) # do not use to_html_stripping_fragment - this is a complete doc
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

    def make_sections(body, is_marker, preserve = lambda _: False, element_name='section', copy=True):
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
                print('marker %s' % current_section['id'])
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
                #x2 = x.__copy__() if copy else x
                x2 = x.__copy__() if copy else x.extract()
                current_section.append(x2)
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

    def is_chapter_or_part_marker(x):
        return is_chapter_marker(x) or is_part_marker(x)
    
    #body = make_sections(body0, is_section_marker, is_chapter_or_part_marker)
    body = make_sections(body0, is_chapter_marker, is_part_marker)
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



#     
#     for tag in main_body.select("a"):
#         href = tag['href']
#         # debug(href)
#         # http://127.0.0.1:8080/libraries/tour1/types.html
#         if href.endswith('html'):
#             page = href.split('/')[-1]
#             new_ref = '#%s' % page
#             tag['href'] = new_ref
