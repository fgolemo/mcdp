
from collections import namedtuple
from contracts.utils import raise_desc, raise_wrapped
from mcdp_cli.solve_meat import solve_main
from mcdp_library import MCDPLibrary
from mcdp_library.libraries import Librarian
from mcdp_library.utils import dir_from_package_name
from mcdp_tests.generation import for_all_source_mcdp
from mocdp import logger
from mocdp.exceptions import DPSemanticError, mcdp_dev_warning
import os
import yaml
from mcdp_web.utils.memoize_simple_imp import memoize_simple  # XXX: move sooner
import tempfile

__all__ = [
    'define_tests_for_mcdplibs',
]

TestLibrary = namedtuple('TestLibrary', 'bigpath librarian short path ')

@memoize_simple
def get_test_librarian():
    package = dir_from_package_name('mcdp_data')
    folder = os.path.join(package, 'libraries')

    if not os.path.exists(folder):
        raise_desc(ValueError, 'Test folders not found.' , folder=folder)

    librarian = Librarian()
    librarian.find_libraries(folder)
    
    libraries = librarian.get_libraries()

    n = len(libraries)
    if n <= 1:
        msg = 'Expected more libraries.'
        raise_desc(ValueError, msg, folder, libraries=libraries)


    return librarian

def enumerate_test_libraries():
    """ Returns list of (bigpath, short_name, path) """
    librarian = get_test_librarian()

    found = []

    libraries = librarian.get_libraries()

    for short, data in libraries.items():
        path = data['path']
        f = os.path.join(path, '.mcdp_test_ignore')
        if os.path.exists(f):
            continue

        found.append(short)

    return found

@memoize_simple
def get_test_library(libname):
    assert isinstance(libname, str) and not 'mcdplib' in libname
    librarian = get_test_librarian()
    library = librarian.load_library(libname)
    d = tempfile.mkdtemp(prefix='mcdplibrary_cache')
    library.use_cache_dir(d)
    # XXX: this does not erase the directory
    return library


def define_tests_for_mcdplibs(context):
    """
        Looks for directories called *.mcdplib in the root of the package.
        
        It also looks for the files *.mcdp_tests.yaml inside.
    """
    librarian = get_test_librarian()

    for libname in enumerate_test_libraries():
        c2 = context.child(libname)

        c2.comp_dynamic(mcdplib_define_tst, libname)
        
        c2.child('ndp').comp_dynamic(mcdplib_test_setup_nameddps, libname=libname)
        c2.child('poset').comp_dynamic(mcdplib_test_setup_posets, libname=libname)
        c2.child('primitivedps').comp_dynamic(mcdplib_test_setup_primitivedps, libname=libname)
        c2.child('source_mcdp').comp_dynamic(mcdplib_test_setup_source_mcdp, libname=libname)

        path = librarian.libraries[libname]['path']
        makefile = os.path.join(path, 'Makefile')
        if os.path.exists(makefile):
            c2.comp(mcdplib_run_make, mcdplib=path)
#
# def load_which(which):
#     assert isinstance(which, tuple) and len(which) == 2
#     bigpath, libname = which
#     librarian = Librarian()
#     librarian.find_libraries(bigpath)
#     library = librarian.get_library(libname)
#     return library


def mcdplib_run_make(mcdplib):
    makefile = os.path.join(mcdplib, 'Makefile')
    assert os.path.exists(makefile)
    cwd = mcdplib
    cmd = ['make', 'clean', 'all']
    from system_cmd.meat import system_cmd_result
    system_cmd_result(cwd, cmd,
                      display_stdout=True,
                      display_stderr=True,
                      raise_on_error=True)
#
# def belongs_to_lib(f, d):
#     """ Returns true if the file is physically inside d
#         and not, for example, symlinked """
#     rf = os.path.realpath(f)
#     rd = os.path.realpath(d)
#     assert os.path.isdir(rd), rd
#     assert not os.path.isdir(rf), rf
#
#     if rd in rf:
#         return True
#     else:
#         return False

def mcdplib_test_setup_nameddps(context, libname):
    """ 
        Loads all mcdp_lang_tests that were specified by comptests
        using the for_all_nameddps decorator. 
    """
    from mcdp_tests import load_tests_modules
    l = get_test_library(libname)
    models = l.get_models()

    from mcdp_tests.generation import for_all_nameddps
    load_tests_modules()
    registered = for_all_nameddps.registered

    print('Found models: %r' % models)
    print('Found registered: %r' % registered)

    for model_name in models:
        f = l._get_file_data(model_name + '.' + MCDPLibrary.ext_ndps)
#         if not belongs_to_lib(f['realpath'], mcdplib):
#             continue
        source = f['data']

        if gives_syntax_error(source):
            print('Skipping because syntax error')
            # TODO: actually check syntax error
        else:
            c = context.child(model_name)

            if gives_semantic_error(source):
                c.comp(mcdplib_assert_semantic_error_fn, libname, model_name,
                       job_id='assert_semantic_error')
            else:
                ndp = c.comp(_load_ndp, libname, model_name, job_id='load_ndp')

                for ftest in registered:
                    c.comp(ftest, model_name, ndp)

def mcdplib_test_setup_source_mcdp(context, libname):
    from mcdp_tests import load_tests_modules

    l = get_test_library(libname)

    load_tests_modules()

    registered = for_all_source_mcdp.registered

    print('Found registered: %r' % registered)

    for basename in l.file_to_contents:
        _model_name, ext = os.path.splitext(basename)
        if ext != ".mcdp":
            # print basename, ext
            continue

        f = l._get_file_data(basename)
#         if not belongs_to_lib(f['realpath'], mcdplib):
#             continue

        source = f['data']

        if gives_syntax_error(source):
            print('Skipping because syntax error')
            # TODO: actually check syntax error
        elif gives_semantic_error(source):
            print('Skipping because semantic error')

        else:            

            c = context.child(basename)
    
            for ftest in registered:
                c.comp(ftest, basename, source)

def get_keywords(source):
    line1 = source.split('\n')[0]
    return line1.split()

def gives_semantic_error(source):
    keywords = get_keywords(source)
    return 'semantic_error' in keywords

def gives_syntax_error(source):
    keywords = get_keywords(source)
    return 'syntax_error' in keywords

def mcdplib_assert_semantic_error_fn(libname, model_name):
    l = get_test_library(libname)
    try:
        res = l.load_ndp(model_name)
        res.abstract()
    except DPSemanticError:
        pass
    except BaseException as e:
        msg = "Expected semantic error, got %s." % type(e)
        raise_wrapped(Exception, e, msg)
    else:
        msg = "Expected an exception, instead succesfull instantiation."
        raise_desc(Exception, msg, model_name=model_name, res=res.repr_long())


def mcdplib_test_setup_posets(context, libname):
    """ 
        Loads all mcdp_lang_tests that were specified by comptests
        using the for_all_nameddps decorator. 
    """
    from mcdp_tests import load_tests_modules

    l = get_test_library(libname)

    posets = l.list_posets()

    from mcdp_tests.generation import for_all_posets
    load_tests_modules()
    registered = for_all_posets.registered

    print('Found posets: %r' % posets)
    print('Found registered: %r' % registered)

    for id_poset in posets:
        c = context.child(id_poset)

        ndp = c.comp(_load_poset, libname, id_poset, job_id='load')

        for ftest in registered:
            c.comp(ftest, id_poset, ndp)


def mcdplib_test_setup_primitivedps(context, libname):
    from mcdp_tests import load_tests_modules
    l = get_test_library(libname)
    dps = l.list_primitivedps()

    from mcdp_tests.generation import for_all_dps
    load_tests_modules()
    registered = for_all_dps.registered

    print('Found: %r' % dps)
    print('Registered: %r' % registered)

    for id_dp in dps:
        c = context.child(id_dp)

        ndp = c.comp(_load_primitivedp, libname, id_dp, job_id='load')

        for ftest in registered:
            c.comp(ftest, id_dp, ndp)

def _load_primitivedp(libname, model_name):
    l = get_test_library(libname)
    return l.load_primitivedp(model_name)

def _load_poset(libname, model_name):
    l = get_test_library(libname)
    return l.load_poset(model_name)

def _load_ndp(libname, model_name):
    l = get_test_library(libname)
    return l.load_ndp(model_name)
    
#
# @contextmanager
# def templib(mcdplib):
#     tmpdir = tempfile.mkdtemp(prefix='mcdplibrary_tmdpir')
#     l = MCDPLibrary()
#
#     l.add_search_dir(mcdplib)
#     l.delete_cache()
#     try:
#         yield l
#     finally:
#         shutil.rmtree(tmpdir)
#



def mcdplib_define_tst(context, libname):
    """
        mcdplib: folder
        
        loads the mcdp_lang_tests in mcdp_tests.yaml
    """
    librarian = get_test_librarian()
    mcdplib = librarian.libraries[libname]['path']

    assert os.path.exists(mcdplib)

    fn = os.path.join(mcdplib, 'mcdp_tests.yaml')
    if not os.path.exists(fn):
        return

    with open(fn) as f:
        data = yaml.load(f)

    if 'test_solve' in data:

        tests = data['test_solve']
        if tests is not None:
            for name, test_data in tests.items():
                c = context.child(name)
                c.comp(mcdplib_define_tst_solve, mcdplib, name, test_data, job_id='solve')


def mcdplib_define_tst_solve(mcdplib, id_test, test_data):  # @UnusedVariable
    mcdp_dev_warning('this doesnt use the librarian')
    # Reload the data (easier to debug)
    fn = os.path.join(mcdplib, 'mcdp_tests.yaml')
    with open(fn) as f:
        data = yaml.load(f)
    test_data = data['test_solve'][id_test]
    
    defaults = dict(lower=None, upper=None, max_steps=None, 
                    intervals=None,
                    expect_nres=None,
                    expect_res=None,
                    imp=None,
                    _exp_advanced=False, expect_nimp=None,
                    plot=False,
                    do_movie=False)
    required = ['query_strings', 'model_name']
    params = defaults.copy()
    for k, v in test_data.items():
        if not k in defaults and not k in required:
            raise_desc(ValueError, 'Invalid configuration.',
                       k=k, test_data=test_data, defaults=defaults)
        params[k] = v
    
    params['logger'] = logger
    params['config_dirs'] = [mcdplib]
    params['out_dir'] = os.path.join(mcdplib + '.out/%s' % id_test)
    params['make'] = False
    solve_main(**params)
