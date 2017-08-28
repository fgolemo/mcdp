# -*- coding: utf-8 -*-
import logging
from mcdp import MCDPConstants, logger, mcdp_dev_warning
from mcdp_library import Librarian
from mcdp_report.html import get_css_filename
import os
from system_cmd import system_cmd_show

from contracts.enabling import disable_all
from contracts.utils import raise_desc
from decent_params import UserError
from quickapp import QuickAppBase

from .minimal_doc import get_minimal_document
from mcdp_utils_xml.parsing import \
    bs_entire_document, to_html_entire_document
from mcdp_docs.manual_join_imp import document_final_pass_after_toc,\
    document_final_pass_before_toc, generate_and_add_toc
from mcdp_docs.add_mathjax import add_mathjax_preamble


class Render(QuickAppBase): 
    """ Render a single document """
    def define_program_options(self, params):
        params.add_string('out', help='Output dir', default=None)

        params.accept_extra()
        params.add_flag('cache')
        params.add_flag('contracts')
        params.add_flag('pdf')
        params.add_flag('forgiving')
        params.add_int('mathjax', help='Use MathJax (requires node)', default=1)
        params.add_string('stylesheet', default='v_mcdp_render_default')
        params.add_string('symbols', default=None)
        params.add_flag('pdf_figures', help='Generate PDF version of code and figures.')

        params.add_string('config_dirs', default='.', short='-D',
                           help='Other libraries.')
        params.add_string('maindir', default='.', short='-d',
                           help='Library directories containing models, separated by :.')

    def go(self):
        logger.setLevel(logging.DEBUG)

        options = self.get_options()

        symbols=self.options.symbols
        if symbols is not None:
            symbols = open(symbols).read()
            
        if not options.contracts:
            disable_all()

        stylesheet = options.stylesheet
        # make sure it exists
        get_css_filename('compiled/%s' % stylesheet)
        
        params = options.get_extra()

        if len(params) < 1:
            raise ValueError('Please specify name.')

        config_dirs = options.config_dirs.split(":")
        maindir = options.maindir
        out_dir = options.out

        if options.cache:
            cache_dir = os.path.join(out_dir, '_cached', 'solve')
        else:
            cache_dir = None
        
        librarian = Librarian()
        for e in config_dirs:
            librarian.find_libraries(e)

        library = librarian.get_library_by_dir(maindir)
        if cache_dir is not None:
            library.use_cache_dir(cache_dir)

        docs = params

        if not docs:
            msg = 'At least one argument required.'
            raise_desc(UserError, msg)

        for docname in docs:
            if '/' in docname:
                docname0 = os.path.split(docname)[-1]
                logger.info("Using %r rather than %r" % (docname0, docname))
                docname = docname0
            suffix =  '.' + MCDPConstants.ext_doc_md
            if docname.endswith(suffix):
                docname = docname.replace(suffix, '')
            basename = docname + suffix
            f = library._get_file_data(basename)
            data = f['data']
            realpath = f['realpath']
            
            generate_pdf = options.pdf_figures
            if out_dir is None:
                use_out_dir = os.path.dirname(realpath)
            else:
                use_out_dir = os.path.join('out', 'mcdp_render')

            raise_errors = not options.forgiving
            use_mathjax = bool(options.mathjax)
            
            html_filename = render(library, docname, data, realpath, use_out_dir, 
                                   generate_pdf, stylesheet=stylesheet,
                                   symbols=symbols, raise_errors=raise_errors,
                                   use_mathjax=use_mathjax)
            if options.pdf:
                run_prince(html_filename)
            

# def add_mathjax_call(s, preamble):
#     soup = BeautifulSoup(s, 'lxml', from_encoding='utf-8')
#     add_mathjax_preamble(soup, preamble)
#     contents2 = str(s)
#     return contents2

def run_prince(html_filename):
    pdf = os.path.splitext(html_filename)[0] + '.pdf'
    cwd = '.'
    cmd = ['prince', 
           '-o', pdf, 
           html_filename] 
    system_cmd_show(cwd, cmd)
    
    cwd = os.getcwd()
    rel = os.path.relpath(pdf, cwd)
    logger.info('Written %s' % rel) 
    
    
def render(library, docname, data, realpath, out_dir, generate_pdf, stylesheet,
           symbols, raise_errors, use_mathjax):
    
    if MCDPConstants.pdf_to_png_dpi < 300:
        msg =( 'Note that pdf_to_png_dpi is set to %d, which is not suitable for printing'
               % MCDPConstants.pdf_to_png_dpi)
        mcdp_dev_warning(msg)


    from mcdp_docs.pipeline import render_complete

    out = os.path.join(out_dir, docname + '.html')
    
    html_contents = render_complete(library=library,
                                    s=data, 
                                    raise_errors=raise_errors, 
                                    raise_missing_image_errors=raise_errors,
                                    realpath=realpath,
                                    generate_pdf=generate_pdf,
                                    symbols=symbols,
                                    use_mathjax=use_mathjax)

    
    title = docname
    
    doc = get_minimal_document(html_contents, title=title, stylesheet=stylesheet,
                               add_markdown_css=True, add_manual_css=True)
    
    soup = bs_entire_document(doc)
    
    document_final_pass_before_toc(soup, remove=None, remove_selectors=[])
    generate_and_add_toc(soup)
    document_final_pass_after_toc(soup)
    
    doc = to_html_entire_document(soup)

    if use_mathjax:
        add_mathjax_preamble(soup, symbols)

    d = os.path.dirname(out)
    if not os.path.exists(d):
        os.makedirs(d)
    with open(out, 'w') as f:
        f.write(doc)

    logger.info('Written %s ' % out)
    return out



mcdp_render_main = Render.get_sys_main()
