import sys

from bs4 import BeautifulSoup
from bs4.element import Tag
from contracts.utils import raise_desc

from .logs import logger


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
    
    
if __name__ == '__main__':
    logger.info('Adding mathjax to all files specified on the command line (overwriting them)')
    
    filenames = sys.argv[1:]
    print filenames
    
    for filename in filenames:
        logger.info('Adding script to %s' % filename)
        contents = open(filename).read()
    
        soup = BeautifulSoup(contents, 'lxml', from_encoding='utf-8')
        add_mathjax_call(soup)
        contents2 = str(soup)
        
        with open(filename, 'w') as f:
            f.write(contents2)
        
            