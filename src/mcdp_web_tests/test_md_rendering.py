# -*- coding: utf-8 -*-
import os
import shutil
import tempfile

from mcdp_library import MCDPLibrary
from mcdp_library.library_utils import list_library_files
from mcdp_library_tests.tests import enumerate_test_libraries, get_test_library
from mcdp_web.renderdoc.highlight import get_minimal_document
from mcdp_web.renderdoc.main import render_complete
from mcdp_web_tests.test_server import test_mcdpweb_server
from mocdp import get_mcdp_tmp_dir
from mocdp.exceptions import mcdp_dev_warning


def define_tests_mcdp_web(context):
    """
        Looks for directories called *.mcdplib in the root of the package.
        
        It also looks for the files *.mcdp_tests.yaml inside.
    """
    for libname in enumerate_test_libraries():
        c2 = context.child(libname)

        c2.comp_dynamic(define_tests_rendering, libname)

        if False:
            c2.comp(test_mcdpweb_server, libname)
        else:
            mcdp_dev_warning('test_mcdpweb_server() is not enabled')


def define_tests_rendering(context, libname):
    library = get_test_library(libname)
    
    ext = MCDPLibrary.ext_doc_md
    for docname, realpath in list_library_files(library, ext):
        job_id = 'render-%s' % docname
        context.comp(check_rendering, libname=libname, filename=realpath, job_id=job_id)


def check_rendering(libname, filename):
    library = get_test_library(libname)
    import codecs
    data = codecs.open(filename, encoding='utf-8').read().encode('utf-8')
    
    mcdp_tmp_dir = get_mcdp_tmp_dir()
    prefix = 'check_rendering'
    tmpdir = tempfile.mkdtemp(dir=mcdp_tmp_dir, prefix=prefix)
  
    try:
        library.use_cache_dir(tmpdir)
    
        contents = render_complete(library, data, raise_errors=True, realpath=filename)
        html = get_minimal_document(contents, add_markdown_css=True)
        
        basename = os.path.basename(filename)
        fn = os.path.join('out', 'check_rendering', libname, basename + '.html')
        d = os.path.dirname(fn)
        if not os.path.exists(d): # pragma: no cover
            os.makedirs(d)
        with open(fn, 'w') as f:
            f.write(html)
        print('written to %r ' % fn)
        
    finally:
        shutil.rmtree(tmpdir)
