# -*- coding: utf-8 -*-
from compmake.utils.friendly_path_imp import friendly_path
from contracts import contract
import getpass
import logging
from mcdp import logger
from mcdp.exceptions import DPSyntaxError
from mcdp_docs.check_bad_input_files import check_bad_input_file_presence
from mcdp_library import MCDPLibrary
from mcdp_library.stdlib import get_test_librarian
from mcdp_utils_misc import expand_all
from mcdp_utils_misc import locate_files, get_md5
import os
import tempfile

from contracts.utils import raise_wrapped
from quickapp import QuickApp
from reprep.utils import natsorted

from .github_edit_links import add_edit_links
from .manual_constants import MCDPManualConstants
from .manual_join_imp import manual_join
from .minimal_doc import get_minimal_document
from .read_bibtex import run_bibtex2html


class RenderManual(QuickApp):
    """ Renders the PyMCDP manual """

    def define_options(self, params):
        params.add_string('src', help="""
        Directories with all contents; separate multiple entries with a colon.""")
        params.add_string('output_file', help='Output file')
        params.add_string('stylesheet', help='Stylesheet', default=None)
        params.add_int('mathjax', help='Use MathJax (requires node)', default=1)
        params.add_string('symbols', help='.tex file for MathJax', default=None)
        params.add_flag('cache')
        params.add_flag('pdf', help='Generate PDF version of code and figures.')
        params.add_string('remove', help='Remove the items with the given selector (so it does not mess indexing)',
                          default=None)
        
    def define_jobs_context(self, context):
        logger.setLevel(logging.DEBUG)

        options = self.get_options()
        src = options.src
        src_dirs = [_ for _ in src.split(":") if _ and _.strip()]
        
#         src_dirs = [expand_all(_) for _ in src_dirs]
        
        out_dir = options.output
        generate_pdf = options.pdf
        output_file = options.output_file
        remove = options.remove
        stylesheet = options.stylesheet
        symbols = options.symbols 
        use_mathjax = True if options.mathjax else False
        
        logger.info('use mathjax: %s' % use_mathjax)
        logger.info('use symbols: %s' % symbols)
        
        if symbols is not None:
            symbols = open(symbols).read()

        bibfile = os.path.join(src_dirs[0], 'bibliography/bibliography.html')

        if out_dir is None:
            out_dir = os.path.join('out', 'mcdp_render_manual')

        for s in src_dirs:
            check_bad_input_file_presence(s)
            
        manual_jobs(context, 
                    src_dirs=src_dirs, 
                    output_file=output_file,
                    generate_pdf=generate_pdf,
                    bibfile=bibfile,
                    stylesheet=stylesheet,
                    remove=remove,
                    use_mathjax=use_mathjax,
                    symbols=symbols,
                    )



@contract(src_dirs='seq(str)', returns='list(str)')
def get_bib_files(src_dirs):
    """ Looks for .bib files in the source dirs; returns list of filenames """
    return look_for_files(src_dirs, "*.bib")

@contract(src_dirs='seq(str)', returns='list(str)')
def get_markdown_files(src_dirs):
    """ Returns a list of filenames. """
    return look_for_files(src_dirs, "*.md")

def look_for_files(srcdirs, pattern):
    """
        Excludes files with "excludes" in the name.
    """
    results = []
    for d0 in srcdirs:  
        d = expand_all(d0)
        if not os.path.exists(d):
            msg = 'Expected directory %s' % d
            raise Exception(msg)
    
        filenames = locate_files(d, pattern, 
                                 followlinks=True,
                                 include_directories=False,
                                 include_files=True,
                                 normalize=False)
        
        ok = []
        for fn in filenames:
            fn = os.path.realpath(fn)
#             fn = os.path.relpath(fn, root)
            if 'exclude' in fn:
                logger.info('Excluding file %r because of string "exclude" in it' % fn)
            else:
                if fn in results:
                    logger.debug('Reached the file %s twice' % fn)
                    pass # 
                else:
                    ok.append(fn)
        results.extend(natsorted(ok))
    
    logger.info('Found %d files in %s' % (len(results), srcdirs))
    return results

    

@contract(src_dirs='seq(str)')
def manual_jobs(context, src_dirs, output_file, generate_pdf, bibfile, stylesheet,
                use_mathjax,
                remove=None, filter_soup=None, extra_css=None, symbols=None):
    """
        src_dirs: list of sources
        symbols: a TeX preamble (or None)
    """
    root_dir = src_dirs[0]
    
    filenames = get_markdown_files(src_dirs)

    if not filenames:
        msg = 'Could not find any file for composing the book.'
        raise Exception(msg)

    files_contents = []
    for i, filename in enumerate(filenames):
        logger.info('adding document %s ' % friendly_path(filename))
        
        docname,_ = os.path.splitext(os.path.basename(filename))
        
        contents = open(filename).read()
        contents_hash = get_md5(contents)[:8] 
        # because of hash job will be automatically erased if the source changes
        out_part_basename = '%03d-%s-%s' % (i, docname, contents_hash)
        job_id = '%s-%s-%s' % (docname, get_md5(filename)[:8], contents_hash)
        
        # find the dir
        for d in src_dirs:
            if os.path.realpath(d) in filename:
                break
        else:
            msg = 'Could not find dir for %s in %s' % (filename, src_dirs)
            
        res = context.comp(render_book, d, docname, generate_pdf,
                           data=contents, realpath=filename,
                           use_mathjax=use_mathjax,
                           symbols=symbols,
                           main_file=output_file,
                           out_part_basename=out_part_basename,
                           filter_soup=filter_soup, 
                           extra_css=extra_css,
                           job_id=job_id)
 
        files_contents.append(res)
    
    bib_files = get_bib_files(src_dirs)
    logger.debug('Found bib files:\n%s' % "\n".join(bib_files))
    if bib_files:
        bib_contents = job_bib_contents(context, bib_files)
        entry  = ('unused', 'bibtex'), bib_contents 
        files_contents.append(entry)
    
    template = get_main_template(root_dir)
   
    d = context.comp(manual_join, template=template, files_contents=files_contents, 
                     stylesheet=stylesheet, remove=remove)
    
    context.comp(write, d, output_file)

    if os.path.exists(MCDPManualConstants.pdf_metadata_template):
        context.comp(generate_metadata, root_dir)

def job_bib_contents(context, bib_files):
    bib_files = natsorted(bib_files)
    # read all contents
    contents = ""
    for fn in bib_files:
        contents += open(fn).read() + '\n\n'
    h = get_md5(contents)[:8]
    job_id = 'bibliography-' + h
    return context.comp(run_bibtex2html, contents, job_id=job_id)

def get_main_template(root_dir):
    fn = os.path.join(root_dir, MCDPManualConstants.main_template)
    if not os.path.exists(fn):
        msg = 'Could not find template %s' % fn 
        raise ValueError(msg)
    
    template = open(fn).read()
    return template

def generate_metadata(src_dir):
    template = MCDPManualConstants.pdf_metadata_template
    if not os.path.exists(template):
        msg = 'Metadata template does not exist: %s' % template
        raise ValueError(msg)

    out = MCDPManualConstants.pdf_metadata
    s = open(template).read()

    from mcdp_docs.pipeline import replace_macros

    s = replace_macros(s)
    with open(out, 'w') as f:
        f.write(s)


def write(s, out):
    dn = os.path.dirname(out)
    if dn != '':
        if not os.path.exists(dn):
            print('creating directory %r for %r' % (dn, out))
            os.makedirs(dn)
    with open(out, 'w') as f:
        f.write(s)
    print('Written %s ' % out)


def render_book(src_dir, docname, generate_pdf, 
                data, realpath,
                main_file, use_mathjax, out_part_basename, filter_soup=None,
                extra_css=None, symbols=None):
    from mcdp_docs.pipeline import render_complete

    librarian = get_test_librarian()
    # XXX: these might need to be changed
    if False:
        librarian.find_libraries('.')
    else:
        if getpass.getuser() == 'andrea':
            logger.error('Remember this might break MCDP')
    
        
    load_library_hooks = [librarian.load_library]
    library = MCDPLibrary(load_library_hooks=load_library_hooks)
    library.add_search_dir(src_dir) 
    
    d = tempfile.mkdtemp()
    library.use_cache_dir(d)

#     basename = docname + '.' + MCDPConstants.ext_doc_md
#     f = library._get_file_data(basename)
#     data = f['data']
#     realpath = f['realpath']

    def filter_soup0(soup, library):
        if filter_soup is not None:
            filter_soup(soup=soup, library=library)
        add_edit_links(soup, realpath)
        
    try:
        html_contents = render_complete(library=library,
                                    s=data, 
                                    raise_errors=True, 
                                    realpath=realpath,
                                    use_mathjax=use_mathjax,
                                    symbols=symbols,
                                    generate_pdf=generate_pdf,
                                    filter_soup=filter_soup0)
    except DPSyntaxError as e:
        msg = 'Could not compile %s' % realpath
        raise_wrapped(DPSyntaxError, e, msg, compact=True)

    doc = get_minimal_document(html_contents,
                               add_markdown_css=True, extra_css=extra_css)
    dirname = main_file + '.parts'
    if dirname and not os.path.exists(dirname):
        try:
            os.makedirs(dirname)
        except:
            pass
    fn = os.path.join(dirname, '%s.html' % out_part_basename)
    with open(fn, 'w') as f:
        f.write(doc)

    return (('unused', out_part_basename), html_contents)

    

mcdp_render_manual_main = RenderManual.get_sys_main()
