import sys

from bs4 import BeautifulSoup, Tag

from contracts.utils import raise_desc

from .logs import logger
import os


def add_mathjax_call(soup):
    head = soup.find('head')
    if not head:
        msg = 'Could not find <head>'
        raise_desc(ValueError, msg, s=str(soup))

    src = 'https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.0/MathJax.js?config=TeX-MML-AM_CHTML'
    
    config = r"""
 MathJax.Hub.Config({
    extensions: ["tex2jax.js"],
    jax: ["input/TeX", "output/HTML-CSS"],
    tex2jax: {
      inlineMath: [ ['$','$'], ],
      displayMath: [ ['$$','$$'], ["\\[","\\]"] ],
      processEscapes: true
    },
    "HTML-CSS": { availableFonts: ["TeX"] }
  });
    """
    script = Tag(name='script')
    script['type'] = 'text/x-mathjax-config'
    script.append(config)
    head.append(script)
    
    script = Tag(name='script')
    script.attrs['src'] = src

    head.append(script)

def add_mathjax_preamble(soup, preamble):
    body = soup.find('body')
    if not body:
        msg = 'Could not find <body> element.'
        raise_desc(ValueError, msg, soup=str(soup)[:200])
        
    div = Tag(name='div')
    div.attrs['id'] = 'mathjax-preamble'
    div.attrs['style'] = 'display: none'
    lines = preamble.split('\n')
    lines = [l for l in lines if l.strip()]
    m = '$$' + "\n".join(lines) +'$$'
    div.append(m)
    
    body.insert(0, div)
    
if __name__ == '__main__':
    logger.info('Adding mathjax to all files specified on the command line (overwriting them)')
    
    preamble = None
    preamble_switch = '--preamble'
    
    args0 = sys.argv[1:]
    args = []
    while args0:
        a = args0.pop(0)
        if a == preamble_switch:
            preamble = args0.pop(0)
        else:
            args.append(a)
        
    filenames = args
#     print filenames
    
    if preamble is not None:
        logger.debug('Reading preamble: %s' % preamble)
        preamble = open(preamble).read()
    else:
        logger.info('No preamble passed (use %r)' % preamble_switch)
    
    for filename in filenames:
        logger.info('Adding mathjax script to %s' % filename)
        
        if not os.path.exists(filename):
            msg = 'Filename does not exist: %s' % filename
            raise Exception(msg)
        
        contents = open(filename).read()
    
        soup = BeautifulSoup(contents, 'lxml', from_encoding='utf-8')
        if preamble is not None:
            add_mathjax_preamble(soup, preamble)
        add_mathjax_call(soup)
        
        contents2 = str(soup)
        
        with open(filename, 'w') as f:
            f.write(contents2)
        
            