from comptests.registrar import run_module_tests, comptest
from mcdp_library.library import MCDPLibrary
from mcdp_docs.pipeline import render_complete
from mcdp_docs.manual_join_imp import manual_join, split_in_files,\
    add_prev_next_links, update_refs, write_split_files, get_id2filename
from mcdp_tests import logger
from bs4 import BeautifulSoup
from bs4.element import Tag
import os

@comptest
def document_split():
    html = get_split_test_document()
    soup = BeautifulSoup(html, 'lxml')
    for e in soup.select('.toc'):
        e.extract()
    html = soup.prettify()
    fn = 'out/document_split.html'
    with open(fn, 'w') as f:
        f.write(html)
    logger.info('written on %s' % fn)
     
    filename2contents = split_in_files(soup)
    id2filename = get_id2filename(filename2contents)
    add_prev_next_links(filename2contents)
    update_refs(filename2contents, id2filename)
        
    linkbase='link.html'
    filename2contents[linkbase] = create_link_base(id2filename)
    
    d = 'out/sec'
    write_split_files(filename2contents, d)

    
#     print html
    
def get_split_test_document():
    md = test_md
    library = MCDPLibrary()
    realpath = 'internal'
    raise_errors = True
    rendered = render_complete(library, md, raise_errors, realpath, generate_pdf=False,
                    check_refs=True, do_math=True, filter_soup=None,
                    raise_missing_image_errors = False)
    
    files_contents = [(('unused', 'unusued'), rendered)]
    bibfile = None
    stylesheet = None
    template = """<html><head><meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>
        </head>
        <style>
        
        </style>
        <body></body></html>
        """
    complete =  manual_join(template, files_contents, bibfile, stylesheet, remove=None, extra_css=None,
                            hook_before_toc=None)
        
    return complete

test_md = """

Preamble (before part starts)

# Aa  {#part:A}

beginning of part A1

# B1

lorem lorem

# B2 marked as draft {.draft}

lorem lorem


## C1

lorem lorem


### D2

lorem lorem


## C2

lorem lorem


# A2  {#part:A2}

beginning of part A2

## A2a also a draft {.draft}

lorem lorem

## Not draft    

    """
if __name__ == '__main__':
    run_module_tests()