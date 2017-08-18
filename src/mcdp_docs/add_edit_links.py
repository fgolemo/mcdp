# -*- coding: utf-8 -*-
import sys

from bs4 import BeautifulSoup
from bs4.element import Tag

from .logs import logger

def add_github_links_if_edit_url(soup):
    """ If an element has an attribute 'github-edit-url' then add little icons """
    attname = 'github-edit-url'
    nfound = 0
    for h in soup.findAll(['h1','h2','h3','h4'], attrs={attname: True}):
        nfound += 1
        s = Tag(name='span')
        a = Tag(name='a')
        a.attrs['href'] = h.attrs[attname]
        a.attrs['class'] = 'github-edit-link'
        a.attrs['title'] = "Click this link to directly edit on the repository."
        a.string = '✎' 
        s.append(a)
        
        a = Tag(name='a')
        hid = h.attrs['id']
        if hid is not None:
            if ':' in hid:
                hid = hid[hid.index(':')+1:]
            url = 'http://purl.org/dth/%s' % hid
            a.attrs['href'] = url
            a.string = '🔗'
            a.attrs['class'] = 'purl-link'
            a.attrs['title'] = "Use this link as the permanent link to share with people."
#             s.append(Tag(name='br')) 
            s.append(a)

        s.attrs['class'] = 'github-etc-links'
        h.insert_after(s)
    
    logger.info('Found %d elements with attribute %r' % (nfound, attname) )

if __name__ == '__main__':
    sys.stderr.write('Loading from stdin...\n')
    
    contents = sys.stdin.read()
#     print ('start: %s  ... %s' % (contents[:100], contents[-100:]))
    soup = BeautifulSoup(contents, 'lxml', from_encoding='utf-8')
#     soup = bs(contents)
#     print 'soup: %s' % soup
    ssoup = str(soup)
#     print ('\n\nstart: %s  ... %s' % (ssoup[:100], ssoup[-100:]))
    
    add_github_links_if_edit_url(soup)
#     print(str(soup)[:0])
    
    contents2 = str(soup)
    
    
    if len(sys.argv) >= 2:
        fn = sys.argv[1]
        sys.stderr.write('Writing to %s\n' % fn)
        with open(fn, 'w') as f:
            f.write(contents2)
    else:
        sys.stderr.write('Writing to stdout\n')
        sys.stdout.write(contents2)
        