# -*- coding: utf-8 -*-
import logging
import os
import tempfile
import time

from contracts import contract
from contracts.utils import check_isinstance, raise_wrapped
from quickapp import QuickApp
from reprep.utils import natsorted

from compmake.context import Context
from compmake.jobs.actions import mark_to_remake
from compmake.jobs.storage import get_job_cache
from compmake.structures import Promise
from mcdp.exceptions import DPSyntaxError
from mcdp_library import MCDPLibrary
from mcdp_library.stdlib import get_test_librarian
from mcdp_utils_misc import locate_files, get_md5

from .github_edit_links import add_edit_links
from .manual_constants import MCDPManualConstants
from .manual_join_imp import manual_join
from .minimal_doc import get_minimal_document
from mcdp import logger


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
def expand_all(x0):
    x = x0
    x = os.path.expanduser(x)
    x = os.path.expandvars(x)
    if '$' in x:
        msg = 'Cannot resolve all environment variables in %r.' % x0
        raise ValueError(msg)
    return x

@contract(srcdirs='seq(str)')
def get_markdown_files(srcdirs):
    """ Returns a hash of 
            nickname -> full path """
    results = []
    for d0 in srcdirs:
        
        d = expand_all(d0)
        if not os.path.exists(d):
            msg = 'Expected directory %s' % d
            raise Exception(msg)
    
        pattern = '*.md'
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

# def make_it_simpler(fn):
#     base = os.getcwd()
#     fn = os.path.realpath(fn)
#     
# 
# def uniq(s):
#     output = []
#     for x in s:
#         if x not in output:
#             output.append(x)
#     return output

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
        logger.info('adding document %s ' % (filename))
        
        docname,_ = os.path.splitext(os.path.basename(filename))
        out_part_basename = '%03d-%s' % (i, docname)
        
        contents = open(filename).read()
        contents_hash = get_md5(contents)[:8] 
        # because of hash job will be automatically erased if the source changes
        job_id = '%s-%s-%s' % (docname, get_md5(filename)[:8], contents_hash)
        res = context.comp(render_book, root_dir, docname, generate_pdf,
                           data=contents, realpath=filename,
                           use_mathjax=use_mathjax,
                           symbols=symbols,
                           main_file=output_file,
                           out_part_basename=out_part_basename,
                           
                           filter_soup=filter_soup, 
                           extra_css=extra_css,
                           job_id=job_id)
 
        files_contents.append(res)
    
    fn = os.path.join(root_dir, MCDPManualConstants.main_template)
    if not os.path.exists(fn):
        msg = 'Could not find template %s' % fn 
        raise ValueError(msg)
    
    template = open(fn).read()
    
    d = context.comp(manual_join, template=template, files_contents=files_contents, 
                     bibfile=bibfile, stylesheet=stylesheet, remove=remove)
    
    context.comp(write, d, output_file)

    if os.path.exists(MCDPManualConstants.pdf_metadata_template):
        context.comp(generate_metadata, root_dir)

    
@contract(compmake_context=Context, promise=Promise, filenames='seq[>=1](str)')
def erase_job_if_files_updated(compmake_context, promise, filenames):
    """ Invalidates the job if the filename is newer """
    check_isinstance(promise, Promise)
    check_isinstance(filenames, (list, tuple))

    def friendly_age(ts):
        age = time.time() - ts
        return '%.3fs ago' % age

    filenames = list(filenames)
    for _ in filenames:
        if not os.path.exists(_):
            msg = 'File does not exist: %s' % _
            raise ValueError(msg)
    last_update = max(os.path.getmtime(_) for _ in filenames)
    db = compmake_context.get_compmake_db()
    job_id = promise.job_id
    cache = get_job_cache(job_id, db)
    if cache.state == cache.DONE:
        done_at = cache.timestamp
        if done_at < last_update:
            show_filenames = filenames if len(filenames) < 3 else '(too long to show)' 
            logger.info('Cleaning job %r because files updated %s' % (job_id, show_filenames))
            logger.info('  files last updated: %s' % friendly_age(last_update))
            logger.info('       job last done: %s' % friendly_age(done_at))

            mark_to_remake(job_id, db)

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
    librarian.find_libraries('.')
        
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
