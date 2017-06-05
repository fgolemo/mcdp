# -*- coding: utf-8 -*-
from compmake.context import Context
from compmake.jobs.actions import mark_to_remake
from compmake.jobs.storage import get_job_cache
from compmake.structures import Promise
from contracts import contract
import logging
from mcdp import MCDPConstants, logger
from mcdp_library.library import MCDPLibrary
from mcdp_library.stdlib import get_test_librarian
from mcdp_utils_misc import locate_files, get_md5
import os
import tempfile
import time

from contracts.utils import check_isinstance
from quickapp import QuickApp
from reprep.utils import natsorted

from .github_edit_links import add_edit_links
from .manual_constants import MCDPManualConstants
from .manual_join_imp import manual_join
from .minimal_doc import get_minimal_document


class RenderManual(QuickApp):
    """ Renders the PyMCDP manual """

    def define_options(self, params):
        params.add_string('src', help='Root directory with all contents')
        params.add_string('output_file', help='Output file')
        params.add_string('stylesheet', help='Stylesheet', default=None)
        params.add_flag('cache')
        params.add_flag('pdf', help='Generate PDF version of code and figures.')
        params.add_string('remove', help='Remove the items with the given selector (so it does not mess indexing)',
                          default=None)
        
    def define_jobs_context(self, context):
        logger.setLevel(logging.DEBUG)

        options = self.get_options()
        src_dir = options.src
        out_dir = options.output
        generate_pdf = options.pdf
        output_file = options.output_file
        remove = options.remove
        stylesheet = options.stylesheet

        bibfile = os.path.join(src_dir, 'bibliography/bibliography.html')

        if out_dir is None:
            out_dir = os.path.join('out', 'mcdp_render_manual')

        manual_jobs(context, 
                    src_dir=src_dir, 
                    output_file=output_file,
                    generate_pdf=generate_pdf,
                    bibfile=bibfile,
                    stylesheet=stylesheet,
                    remove=remove,
                    )
        
def get_manual_contents(srcdir):
    root = os.getcwd()
    directory = os.path.join(root, srcdir)
    if not os.path.exists(directory):
        msg = 'Expected directory %s' % directory
        raise Exception(msg)
    pattern = '*.md'
    filenames = locate_files(directory, pattern, followlinks=True,
                 include_directories=False,
                 include_files=True,
                 normalize=False)
    ok = []
    for fn in filenames:
        fn = os.path.relpath(fn, root)
        if 'exclude' in fn:
            logger.info('Excluding file %r because of string "exclude" in it' % fn)
            continue
        ok.append(fn)
    filenames = natsorted(ok)
    for f in filenames:
        docname, _extension = os.path.splitext(os.path.basename(f))
        yield 'manual', docname


def manual_jobs(context, src_dir, output_file, generate_pdf, bibfile, stylesheet, 
                remove=None, filter_soup=None, extra_css=None):
    manual_contents = list(get_manual_contents(src_dir))

    if not manual_contents:
        msg = 'Could not find any file for composing the book.'
        raise Exception(msg)

    # check that all the docnames are unique
    pnames = [_[1] for _ in manual_contents]
    if len(pnames) != len(set(pnames)):
        msg = 'Repeated names detected: %s' % pnames
        raise ValueError(msg)

    local_files = list(locate_files(src_dir, '*.md'))
    basename2filename = dict( (os.path.basename(_), _) for _ in local_files)

    files_contents = []
    for i, (_, docname) in enumerate(manual_contents):
        libname = 'unused'
        logger.info('adding document %s - %s' % (libname, docname))
        out_part_basename = '%02d%s' % (i, docname)
        
        # read the file to get hash
        basename = '%s.md' % docname
        fn = basename2filename[basename]
        contents = open(fn).read()
        contents_hash = get_md5(contents)[:8] 
        # job will be automatically erased if the source changes
        job_id = '%s-%s' % (docname,contents_hash)
        res = context.comp(render_book, src_dir, docname, generate_pdf,
                           
                           main_file=output_file,
                           out_part_basename=out_part_basename,
                           
                           filter_soup=filter_soup, 
                           extra_css=extra_css,
                           job_id=job_id)

#         source = '%s.md' % docname
#         if source in basename2filename:
#             filenames = [basename2filename[source]]
#             erase_job_if_files_updated(context.cc, promise=res,
#                                        filenames=filenames)
#         else:
#             logger.debug('Could not find file %r for date check' % source)

        files_contents.append(res)

    fn = os.path.join(src_dir, MCDPManualConstants.main_template)
    if not os.path.exists(fn):
        msg = 'Could not find template %s' % fn 
        raise ValueError(msg)
    
    template = open(fn).read()
    

    d = context.comp(manual_join, template=template, files_contents=files_contents, 
                     bibfile=bibfile, stylesheet=stylesheet, remove=remove)
    context.comp(write, d, output_file)

    if os.path.exists(MCDPManualConstants.pdf_metadata_template):
        context.comp(generate_metadata, src_dir)

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


def render_book(src_dir, docname, generate_pdf, main_file, out_part_basename, filter_soup=None,
                extra_css=None):
    from mcdp_docs.pipeline import render_complete

    librarian = get_test_librarian()
    librarian.find_libraries('.')
        
    load_library_hooks = [librarian.load_library]
    library = MCDPLibrary(load_library_hooks=load_library_hooks)
    library.add_search_dir(src_dir)
# 
#     data = dict(path=dirname, library=l)
#     l.library_name = library_name
#     
#     library = librarian.load_library(libname)
#     
#     l = library.load_library(libname)
    
    d = tempfile.mkdtemp()
    library.use_cache_dir(d)

    basename = docname + '.' + MCDPConstants.ext_doc_md
    f = library._get_file_data(basename)
    data = f['data']
    realpath = f['realpath']


    def filter_soup0(soup, library):
        if filter_soup is not None:
            filter_soup(soup=soup, library=library)
        add_edit_links(soup, realpath)
        
    html_contents = render_complete(library=library,
                                    s=data, 
                                    raise_errors=True, 
                                    realpath=realpath,
                                    generate_pdf=generate_pdf,
                                    filter_soup=filter_soup0)

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

    return (('unused', docname), html_contents)

    

mcdp_render_manual_main = RenderManual.get_sys_main()
