from contextlib import contextmanager
import logging
from mcdp import logger
from mcdp_docs.add_mathjax import add_mathjax_call, add_mathjax_preamble
from mcdp_docs.manual_join_imp import update_refs_
from mcdp_utils_misc.string_utils import get_md5
from mcdp_utils_xml import bs
import os
import time

from bs4 import BeautifulSoup
from bs4.element import Tag
from quickapp import QuickApp

from .manual_join_imp import add_prev_next_links, split_in_files, get_id2filename, create_link_base
from .split_disqus import append_disqus


show_timing = False

@contextmanager
def timeit(s):
    t0 = time.clock()
    yield
    delta = time.clock() - t0
    if show_timing:
        logger.debug('%10d ms: %s' % ( 1000*delta, s))
    
def make_page(contents, head0, main_toc):
    """ Returns html """
    html = Tag(name='html')
    
    head = head0.__copy__()
    html.append(head)
    body = Tag(name='body')
    
    with timeit('make_page() / copy toc'):
        if main_toc:
            tocdiv = Tag(name='div')
            tocdiv.attrs['id'] = 'tocdiv' 

            toc = main_toc
            toc.extract()
            del toc.attrs['id']
            tocdiv.append(toc)
            
    body.append(tocdiv)
    not_toc = Tag(name='div')
    not_toc.attrs['id'] = 'not-toc'
    not_toc.append(contents)
    body.append(not_toc)
    html.append(body)
    return html

def split_file(ifilename, directory, filename, mathjax, preamble, disqus, id2filename):
    html = open(ifilename).read()
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
    
    with timeit('Splitting in files...'):
        filename2contents = split_in_files(body)
    
    with timeit('add_prev_next_links()...'):
        filename2contents = add_prev_next_links(filename2contents)
    

    with timeit('make_page()'):
        contents = filename2contents[filename]
        html = make_page(contents, head0, main_toc)
    
    
    if mathjax: 
        if preamble is not None:
            with timeit('add_mathjax_preamble()'):
                add_mathjax_preamble(html, preamble)
            
            
        with timeit('add_mathjax_call'):
            add_mathjax_call(html)
        
    
    if disqus:
        with timeit('disqus'):
            append_disqus(filename, html)
        
         

    with timeit('update_refs_'):
        update_refs_(filename, html, id2filename)


    with timeit('serialize'):
        result = str(html)
    
    with timeit('writing'): 
        
        if not os.path.exists(directory):
            try:
                os.makedirs(directory)
            except:
                pass
        fn = os.path.join(directory, filename)
        with open(fn, 'w') as f:
            f.write(result)
    logger.info('written section to %s' % fn)
    


class Split(QuickApp):
    """ Splits the manual into files """

    def define_options(self, params):
        params.add_string('filename', help="""Input filename""")
        params.add_string('output_dir', help='Output directory')
        params.add_flag('disqus')
        params.add_flag('mathjax')
        params.add_string('preamble', default=None)
        
    def define_jobs_context(self, context):
        ifilename = self.options.filename
        output_dir = self.options.output_dir
        mathjax = self.options.mathjax
        preamble = self.options.preamble
        disqus = self.options.disqus
        logger.setLevel(logging.DEBUG)
    
        html = open(ifilename).read()
        soup = BeautifulSoup(html, 'lxml', from_encoding='utf-8')
        body = soup.html.body
        filename2contents = split_in_files(body)
        
        if not os.path.exists(output_dir):
            try:
                os.makedirs(output_dir)
            except:
                pass
        
        id2filename = get_id2filename(filename2contents)
        linkbase = 'link.html'
        lb = create_link_base(id2filename)
        with open(os.path.join(output_dir, linkbase), 'w') as f:
            f.write(str(lb)) 

        if preamble:
            preamble = open(preamble).read()
            
        ids = sorted(id2filename)
        data = "".join(id2filename[_] for _ in ids)
        links_hash = get_md5(data)[:8]
        
        for filename, contents in filename2contents.items():
            contents_hash = get_md5(str(contents) + preamble)[:8]
            # logger.info('Set up %r' % filename)
            job_id = '%s-%s-%s' % (filename, links_hash, contents_hash)
            context.comp(split_file, ifilename, output_dir, filename, mathjax=mathjax, preamble=preamble,
                         disqus=disqus, id2filename=id2filename,
                         job_id=job_id)

split_main = Split.get_sys_main()

