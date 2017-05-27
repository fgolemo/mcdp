# -*- coding: utf-8 -*-
import codecs
from contextlib import contextmanager
from mcdp import MCDPConstants, logger
from mcdp.exceptions import mcdp_dev_warning, DPSyntaxError
from mcdp_docs.minimal_doc import get_minimal_document
from mcdp_docs.pipeline import render_complete
from mcdp_library.library_utils import list_library_files
from mcdp_library_tests.tests import enumerate_test_libraries, get_test_library
from mcdp_utils_misc.fileutils import get_mcdp_tmp_dir
from mcdp_web_tests.test_server import test_mcdpweb_server
import os
import shutil
import tempfile

from contracts.utils import check_isinstance


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
    
    ext = MCDPConstants.ext_doc_md
    for docname, realpath in list_library_files(library, ext):
        job_id = 'render-%s' % docname
        context.comp(check_rendering, libname=libname, filename=realpath, job_id=job_id)

def read_file_encoded_as_utf8(filename):
    u = codecs.open(filename, encoding='utf-8').read()
    s = u.encode('utf-8')
    return s

    
def write_file_encoded_as_utf8(filename, data):
    check_isinstance(data, str)

    d = os.path.dirname(filename)
    if not os.path.exists(d): # pragma: no cover
        os.makedirs(d)

    u = unicode(data, 'utf-8')
    with codecs.open(filename, encoding='utf-8') as f:
        f.write(u)
        
    logger.debug('Written %s' % filename)
    
def get_expected_exceptions(markdown_data):
    expected = []
    first_line = markdown_data.split('\n')[0]
    expect_syntax_error = 'syntax_error' in first_line
    if expect_syntax_error:
        expected.append(DPSyntaxError)
        logger.info('Expecting DPSyntaxError')
    expected = tuple(expected)
    return expected
  
def check_rendering(libname, filename):
    library = get_test_library(libname)
    data = read_file_encoded_as_utf8(filename)
    
    expected = get_expected_exceptions(data)
    
    with with_library_cache_dir(library):
        try:
            contents = render_complete(library, data, 
                                       raise_errors=True, realpath=filename)
            # write html
            html = get_minimal_document(contents, add_markdown_css=True)        
            basename = os.path.basename(filename)
            fn = os.path.join('out', 'check_rendering', libname, basename + '.html')
            write_file_encoded_as_utf8(fn, html)
        except expected:
            return
        
    
@contextmanager
def with_library_cache_dir(library, prefix='with_library_cache_dir'):
    mcdp_tmp_dir = get_mcdp_tmp_dir()
    tmpdir = tempfile.mkdtemp(dir=mcdp_tmp_dir, prefix=prefix)
    library.use_cache_dir(tmpdir)
    
    try: 
        yield
    except:
        logger.debug('Keeping %s' % tmpdir)
        pass
    else:
        shutil.rmtree(tmpdir)

