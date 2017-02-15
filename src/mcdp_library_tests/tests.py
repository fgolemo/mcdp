# -*- coding: utf-8 -*-
import math
import os
import tempfile

from contracts.enabling import all_disabled
from contracts.utils import raise_desc, raise_wrapped
from mcdp.utils.timing import timeit
from mcdp_library import MCDPLibrary
from mcdp_library.stdlib import get_test_librarian
from mcdp_tests import get_test_index
from mcdp_tests.generation import for_all_source_mcdp,\
    for_all_source_mcdp_template, for_all_source_mcdp_poset,\
    for_all_source_mcdp_value, for_all_source_all
from mocdp import logger, get_mcdp_tmp_dir
from mocdp.comp.context import Context
from mocdp.exceptions import DPSemanticError, DPNotImplementedError
from mcdp.utils.memoize_simple_imp import memoize_simple  # XXX: move sooner


__all__ = [
    'define_tests_for_mcdplibs',
]

def testing_includes(libname):
    librarian = get_test_librarian()
    return libname in librarian.get_libraries()
    
def enumerate_test_libraries():
    """ 
        Libraries on which we need to run tests. 
    
    Returns list of (bigpath, short_name, path) """
    librarian = get_test_librarian()

    found = []

    libraries = librarian.get_libraries()

    for short in list(libraries):
        data = libraries[short]
        path = data['path']
        f = os.path.join(path, '.mcdp_test_ignore')
        if os.path.exists(f):
            continue

        found.append(short)

    i, n = get_test_index()
    if n == 1:
        uselibs = found
    else:
        assert n > 1
        # 0 only gets the basic tests
        if i == 0:
            return []
        else:
            n_effective = n - 1
            i_effective = i - 1
            assert 0 <= i_effective < n_effective
            
            uselibs = []
            buckets = [ [] for _ in range(n_effective)] 
            
            for j, libname in enumerate(found):
                #do = j % n_effective == i_effective
                which = int(math.floor((float(j) / len(found)) * n_effective))
                
                assert 0 <= which < n_effective, (j, which, n_effective)
                buckets[which].append(libname)
                 
#                 do = math.floor((j - 1) / n_effective) == i_effective
            for libname in found:
                do = libname in buckets[i_effective]
                if do:
                    uselibs.append(libname)
                    s = 'will do'
                else:
                    s = 'skipped because of parallelism'
                logger.debug('%20s: %s' % (libname, s))
                
            
            ntot = sum(len(_) for _ in buckets)
            assert ntot == len(found)
            
        
    return uselibs


@memoize_simple
def get_test_library(libname):
    assert isinstance(libname, str) and not 'mcdplib' in libname
    librarian = get_test_librarian()
    library = librarian.load_library(libname)
    
    d = get_mcdp_tmp_dir()
    prefix = 'mcdp_library_tests_get_test_library_'
    d = tempfile.mkdtemp(dir=d, prefix=prefix)

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
        
        c2 = context.child(libname, extra_report_keys=dict(libname=libname))

        c2.child('ndp').comp_dynamic(mcdplib_test_setup_nameddps, libname=libname)
        c2.child('poset').comp_dynamic(mcdplib_test_setup_posets, libname=libname)
        c2.child('primitivedp').comp_dynamic(mcdplib_test_setup_primitivedps, libname=libname)
        c2.child('source_mcdp').comp_dynamic(mcdplib_test_setup_sources, libname=libname)
        c2.child('value').comp_dynamic(mcdplib_test_setup_value, libname=libname)
        c2.child('template').comp_dynamic(mcdplib_test_setup_template, libname=libname)

        path = librarian.libraries[libname]['path']
        makefile = os.path.join(path, 'Makefile')
        if os.path.exists(makefile):
            c2.comp(mcdplib_run_make, mcdplib=path)


def mcdplib_run_make(mcdplib):
    makefile = os.path.join(mcdplib, 'Makefile')
    assert os.path.exists(makefile)
    cwd = mcdplib
    cmd = [
        'make', 
        'clean', 
        'all',
    ]
    # do not use too many resources
    circle = 'CIRCLECI' in os.environ
    parallel = not circle
    if parallel:
        cmd.append('-j')
        
    from system_cmd.meat import system_cmd_result
    logger.debug('$ cd %s' % cwd)
    env = os.environ.copy()
    if all_disabled():
        env['DISABLE_CONTRACTS'] = '1'
        msg = ('Disabling contracts in environment by adding '
               'DISABLE_CONTRACTS=%r.' % env['DISABLE_CONTRACTS'])
        logger.debug(msg)
        
    system_cmd_result(cwd, cmd,
                      display_stdout=True,
                      display_stderr=True,
                      raise_on_error=True,
                      env=env)


def mcdplib_test_setup_nameddps(context, libname):
    """ 
        Loads all mcdp_lang_tests that were specified by comptests
        using the for_all_nameddps decorator. 
    """
    from mcdp_tests import load_tests_modules
    l = get_test_library(libname)
    models = l.get_models()

    from mcdp_tests.generation import for_all_nameddps, for_all_nameddps_dyn
    load_tests_modules()

    if False:
        print('Found models: %r' % models)
        print('Found registered in for_all_nameddps_dyn: %r' % 
              for_all_nameddps.registered)
        print('Found registered in for_all_nameddps: %r' % 
              for_all_nameddps_dyn.registered)

    for model_name in models:
        f = l._get_file_data(model_name + '.' + MCDPLibrary.ext_ndps)

        source = f['data']

        if gives_syntax_error(source):
            #print('Skipping because syntax error')
            # TODO: actually check syntax error
            pass
        else:
            c = context.child(model_name, extra_report_keys=dict(id_ndp=model_name))

            if gives_not_implemented_error(source):
                c.comp(mcdplib_assert_not_implemented_error_fn, libname, model_name,
                       job_id='assert_not_implemented_error')
            elif gives_semantic_error(source):
                c.comp(mcdplib_assert_semantic_error_fn, libname, model_name,
                       job_id='assert_semantic_error')
            else:
                ndp = c.comp(_load_ndp, libname, model_name, job_id='load')

                    
                for ftest in for_all_nameddps.registered:
                    
                    if accepts_arg(ftest, 'libname'):
                        #print('using libname for %s' % ftest)
                        c.comp(ftest, model_name, ndp, libname=libname,
                               job_id=ftest.__name__)
                    else:
                        c.comp(ftest, model_name, ndp)
                        
                for ftest in for_all_nameddps_dyn.registered:
                    
                    if accepts_arg(ftest, 'libname'):
                        #print('using libname for %s' % ftest)
                        c.comp_dynamic(ftest, model_name, ndp, libname=libname,
                                       job_id=ftest.__name__)
                    else:
                        c.comp_dynamic(ftest, model_name, ndp)
                        
                     
    
def accepts_arg(f, name):
    """ True if the function f supports the "name" argument """
    import inspect
    args = inspect.getargspec(f)
    return name in args.args

def mcdplib_test_setup_sources(context, libname):
    from mcdp_tests import load_tests_modules

    l = get_test_library(libname)

    load_tests_modules()

    types = [
        (['mcdp','mcdp_template','mcdp_poset','mcdp_value'], for_all_source_all),
        (['mcdp'], for_all_source_mcdp),
        (['mcdp_template'], for_all_source_mcdp_template),
        (['mcdp_poset'], for_all_source_mcdp_poset),
        (['mcdp_value'], for_all_source_mcdp_value),
    ]
    for extensions, accumulator in types:
        mcdplib_test_setup_sources_(context, libname, l, extensions, accumulator)
        
def mcdplib_test_setup_sources_(context, libname, l, extensions, accumulator):
    registered = accumulator.registered

    #print('Found registered: %r' % registered)

    for basename in l.file_to_contents:
        _model_name, dotext = os.path.splitext(basename)
        ext = dotext[1:] # remove '.'
        if not ext in extensions:
            continue

        f = l._get_file_data(basename) 

        source = f['data']
        filename = f['realpath']

        if gives_syntax_error(source):
            #print('Skipping because syntax error')
            pass
            # TODO: actually check syntax error
        elif gives_semantic_error(source):
            # print('Skipping because semantic error')
            pass

        else:            

            c = context.child(basename)
             
            for ftest in registered:
                kwargs = {}
                if accepts_arg(ftest, 'libname'):
                    kwargs['libname'] = libname
                c.comp(ftest, filename, source, **kwargs)

def get_keywords(source):
    line1 = source.split('\n')[0]
    return line1.split()

def gives_semantic_error(source):
    keywords = get_keywords(source)
    return 'semantic_error' in keywords

def gives_not_implemented_error(source):
    keywords = get_keywords(source)
    return 'not_implemented_error' in keywords

def gives_syntax_error(source):
    keywords = get_keywords(source)
    return 'syntax_error' in keywords

def mcdplib_assert_not_implemented_error_fn(libname, model_name):
    l = get_test_library(libname)
    try:
        res = l.load_ndp(model_name)
        res.abstract()
    except DPNotImplementedError:
        pass
    except BaseException as e:
        msg = "Expected DPNotImplementedError, got %s." % type(e)
        raise_wrapped(Exception, e, msg)
    else:
        msg = "Expected DPNotImplementedError, instead succesfull instantiation."
        raise_desc(Exception, msg, model_name=model_name, res=res.repr_long())
    
def mcdplib_assert_semantic_error_fn(libname, model_name):
    l = get_test_library(libname)
    try:
        res = l.load_ndp(model_name)
        res.abstract()
    except DPSemanticError:
        pass
    except BaseException as e:
        msg = "Expected DPSemanticError, got %s." % type(e)
        raise_wrapped(Exception, e, msg)
    else:
        msg = "Expected DPSemanticError, instead succesfull instantiation."
        raise_desc(Exception, msg, model_name=model_name, res=res.repr_long())

def mcdplib_test_setup_value(context, libname):
    from mcdp_tests import load_tests_modules

    l = get_test_library(libname)

    values = l.list_values()

    from mcdp_tests.generation import for_all_values
    load_tests_modules()
    registered = for_all_values.registered

    #print('Found values: %r' % values)
    #print('Found registered: %r' % registered)

    for id_value in values:
        c = context.child(id_value)

        ndp = c.comp(_load_value, libname, id_value, job_id='load')

        for ftest in registered:
            c.comp(ftest, id_value, ndp)

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

    #print('Found posets: %r' % posets)
    #print('Found registered: %r' % registered)

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

    #print('Found: %r' % dps)
    #print('Registered: %r' % registered)

    for id_dp in dps:
        c = context.child(id_dp)

        ndp = c.comp(_load_primitivedp, libname, id_dp, job_id='load')

        for ftest in registered:
            c.comp(ftest, id_dp, ndp)

def mcdplib_test_setup_template(context, libname):
    from mcdp_tests import load_tests_modules
    l = get_test_library(libname)
    templates = l.list_templates()

    from mcdp_tests.generation import for_all_templates
    load_tests_modules()
    registered = for_all_templates.registered

    #print('Found: %r' % templates)
    #print('Registered: %r' % registered)

    for id_template in templates:
        c = context.child(id_template)

        ndp = c.comp(_load_template, libname, id_template, job_id='load')

        for ftest in registered:
            c.comp(ftest, id_template, ndp)

    
min_time_warn = 0.5

def _load_primitivedp(libname, model_name):
    context = Context()
    l = get_test_library(libname)
    with timeit(model_name, minimum=min_time_warn):
        return l.load_primitivedp(model_name, context)

def _load_template(libname, model_name):
    context = Context()
    l = get_test_library(libname)
    with timeit(model_name, minimum=min_time_warn):
        return l.load_template(model_name, context)

def _load_value(libname, name):
    l = get_test_library(libname)
    context = Context()
    with timeit(name, minimum=min_time_warn):
        vu = l.load_constant(name, context)
    return vu

def _load_poset(libname, model_name):
    l = get_test_library(libname)
    context = Context()
    with timeit(model_name, minimum=min_time_warn):
        return l.load_poset(model_name, context)

def _load_ndp(libname, model_name):
    l = get_test_library(libname)
    context = Context() 
    with timeit(model_name, minimum=min_time_warn):
        return l.load_ndp(model_name, context)
    
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


