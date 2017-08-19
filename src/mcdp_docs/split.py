import sys
import os

from bs4 import BeautifulSoup
from bs4.element import Tag

from mcdp import logger
from mcdp_utils_xml import bs

from .manual_join_imp import get_id2filename, create_link_base
from .manual_join_imp import write_split_files, add_prev_next_links,\
    split_in_files, update_refs
from .split_disqus import append_disqus


def make_page(contents, head0, main_toc):
    """ Returns html """
    html = Tag(name='html')
    head = head0.__copy__()
    html.append(head)
    body = Tag(name='body')
    if main_toc:
        tocdiv = Tag(name='div')
        tocdiv.attrs['id'] = 'tocdiv'
        toc = main_toc.__copy__()
        del toc.attrs['id']
        tocdiv.append(toc)
    body.append(tocdiv)
    not_toc = Tag(name='div')
    not_toc.attrs['id'] = 'not-toc'
    not_toc.append(contents)
    body.append(not_toc)
    html.append(body)
    return html

def split_file(html, directory):
    soup = BeautifulSoup(html, 'lxml', from_encoding='utf-8')
    body = soup.html.body
    head0 = soup.html.head
    # extract the main toc if it is there
    main_toc = body.find(id='main_toc')
    if main_toc is None:
        msg = 'No element #main_toc'
        raise ValueError(msg)

    p = bs('<p><a href="index.html">Home</a></p>')
    main_toc.insert(0, p.p)

    assert body is not None, soup
    logger.debug('Splitting in files...')
    filename2contents = split_in_files(body)
    id2filename = get_id2filename(filename2contents)
    logger.debug('add_prev_next_links()...')
    filename2contents = add_prev_next_links(filename2contents)
    logger.debug('adding_toc()...')
    for filename, contents in list(filename2contents.items()):
        logger.debug('%s: make_page()' % os.path.basename(filename))
        html = make_page(contents, head0, main_toc)
        logger.debug('%s: append_disqus' % os.path.basename(filename))
        append_disqus(filename, html)
        filename2contents[filename] = html

    logger.debug('update_refs()...')

    update_refs(filename2contents, id2filename)

    linkbase='link.html'
    filename2contents[linkbase] = create_link_base(id2filename)
    logger.debug('write_split_files()...')
    write_split_files(filename2contents, directory)


if __name__ == '__main__':
    filename = sys.argv[1]
    directory = sys.argv[2]
    html = open(filename).read()

    split_file(html, directory)
