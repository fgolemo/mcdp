from mcdp_library.library import MCDPLibrary
from mcdp_library.library_utils import list_library_files
from mcdp_library_tests.tests import enumerate_test_libraries
from mcdp_web.renderdoc.main import render_complete
from mcdp_web_tests.test_server import test_mcdpweb_server
import shutil
import tempfile


def define_tests_mcdp_web(context):
    """
        Looks for directories called *.mcdplib in the root of the package.
        
        It also looks for the files *.mcdp_tests.yaml inside.
    """
    for short, dirname in enumerate_test_libraries():
        c2 = context.child(short)
        c2.comp_dynamic(define_tests_rendering, dirname)
        c2.comp(test_mcdpweb_server, dirname)


def define_tests_rendering(context, dirname):
    library = MCDPLibrary()
    library.add_search_dir(dirname)
    
    ext = MCDPLibrary.ext_doc_md
    for docname, realpath in list_library_files(library, ext):
        job_id = 'render-%s' % docname
        context.comp(check_rendering, dirname, docname, realpath, job_id=job_id)


def check_rendering(dirname, docname, filename):  # @UnusedVariable
    import codecs
    data = codecs.open(filename, encoding='utf-8').read().encode('utf-8')

    library = MCDPLibrary()
    library.add_search_dir(dirname)
    
    tmpdir = tempfile.mkdtemp(prefix='mcdplibrary_cache')
    library.use_cache_dir(tmpdir)

    render_complete(library, data, raise_errors=True, realpath=filename)

    shutil.rmtree(tmpdir)
