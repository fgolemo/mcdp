from conf_tools.utils.locate_files_imp import locate_files
from conf_tools.utils.resources import dir_from_package_name
from contracts.utils import raise_desc
from mcdp_cli.solve_meat import solve_main
from mcdp_library.library import MCDPLibrary
from mocdp import logger
import os
import yaml
from contextlib import contextmanager
import tempfile
import shutil

__all__ = [
    'define_tests_for_mcdplibs',
]


def define_tests_for_mcdplibs(context):
    """
        Looks for directories called *.mcdplib in the root of the package.
        
        It also looks for the files *.mcdp_tests.yaml inside.
    """

    folder = os.path.join(dir_from_package_name('mocdp'), '..', '..', '..')

    if not os.path.exists(folder):
        raise_desc(ValueError, 'No tests found.' , folder=folder)

    mcdplibs = locate_files(folder, '*.mcdplib', include_directories=True,
                            include_files=False)
    n = len(mcdplibs)
    if n <= 1:
        msg = 'Expected more tests.'
        raise_desc(ValueError, msg, folder, mcdplibs=mcdplibs)

    # c = context.child('mcdplib')
    c = context
    for m in mcdplibs:
        short = os.path.splitext(os.path.basename(m))[0]
        short = short.replace('.', '_')
        c2 = c.child(short)
        c2.comp_dynamic(mcdplib_define_tst, mcdplib=m)
        
        c2.child('ndp').comp_dynamic(mcdplib_test_setup_nameddps, mcdplib=m)
        c2.child('poset').comp_dynamic(mcdplib_test_setup_posets, mcdplib=m)
        c2.child('primitivedps').comp_dynamic(mcdplib_test_setup_primitivedps, mcdplib=m)

        makefile = os.path.join(m, 'Makefile')
        if os.path.exists(makefile):
            c2.comp(mcdplib_run_make, mcdplib=m)
        else:
            logger.warn('No makefile in %r.' % m)
            

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


def mcdplib_test_setup_nameddps(context, mcdplib):
    """ 
        Loads all tests that were specified by comptests
        using the for_all_nameddps decorator. 
    """
    from mocdp import load_tests_modules

    l = MCDPLibrary()
    l.add_search_dir(mcdplib)
    models = l.get_models()

    from mocdp.unittests.generation import for_all_nameddps
    load_tests_modules()
    registered = for_all_nameddps.registered

    print('Mcdplib: %s' % mcdplib)
    print('Found models: %r' % models)
    print('Found registered: %r' % registered)

    for model_name in models:
        c = context.child(model_name)

        ndp = c.comp(_load_ndp, mcdplib, model_name, job_id='load_ndp')

        for ftest in registered:
            c.comp(ftest, model_name, ndp)



def mcdplib_test_setup_posets(context, mcdplib):
    """ 
        Loads all tests that were specified by comptests
        using the for_all_nameddps decorator. 
    """
    from mocdp import load_tests_modules

    l = MCDPLibrary()
    l.add_search_dir(mcdplib)
    posets = l.list_posets()

    from mocdp.unittests.generation import for_all_posets
    load_tests_modules()
    registered = for_all_posets.registered

    print('Mcdplib: %s' % mcdplib)
    print('Found posets: %r' % posets)
    print('Found registered: %r' % registered)

    for id_poset in posets:
        c = context.child(id_poset)

        ndp = c.comp(_load_poset, mcdplib, id_poset, job_id='load_poset')

        for ftest in registered:
            c.comp(ftest, id_poset, ndp)


def mcdplib_test_setup_primitivedps(context, mcdplib):
    from mocdp import load_tests_modules

    l = MCDPLibrary()
    l.add_search_dir(mcdplib)
    dps = l.list_primitivedps()

    from mocdp.unittests.generation import for_all_dps
    load_tests_modules()
    registered = for_all_dps.registered

    print('Mcdplib: %s' % mcdplib)
    print('Found: %r' % dps)
    print('Registered: %r' % registered)

    for id_dp in dps:
        c = context.child(id_dp)

        ndp = c.comp(_load_primitivedp, mcdplib, id_dp, job_id='load_poset')

        for ftest in registered:
            c.comp(ftest, id_dp, ndp)

def _load_primitivedp(mcdplib, model_name):
    with templib(mcdplib) as l:
        return l.load_primitivedp(model_name)

def _load_poset(mcdplib, model_name):
    with templib(mcdplib) as l:
        return l.load_poset(model_name)

def _load_ndp(mcdplib, model_name):
    with templib(mcdplib) as l:
        return l.load_ndp(model_name)

@contextmanager
def templib(mcdplib):
    tmpdir = tempfile.mkdtemp(prefix='mcdplibrary_tmdpir')
    l = MCDPLibrary()

    l.add_search_dir(mcdplib)
    l.delete_cache()
    try:
        yield l
    finally:
        shutil.rmtree(tmpdir)
    



def mcdplib_define_tst(context, mcdplib):
    """
        mcdplib: folder
        
        loads the tests in mcdp_tests.yaml
    """
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


def mcdplib_define_tst_solve(mcdplib, id_test, test_data):
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

    solve_main(**params)
