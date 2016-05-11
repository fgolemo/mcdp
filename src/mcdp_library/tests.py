from cdpview.solve_meat import solve_main
from conf_tools.utils.locate_files_imp import locate_files
from conf_tools.utils.resources import dir_from_package_name
from contracts.utils import raise_desc
from mocdp import logger
import os
import yaml

__all__ = [
    'define_tests_for_mcdplibs',
]


def define_tests_for_mcdplibs(context):
    """
        Looks for directories called *.mcdplib.
        and files *.mcdp_tests.yaml inside
    """

    folder = os.path.join(dir_from_package_name('mocdp'), '..', '..', 'examples-drone1')
    if not os.path.exists(folder):
        raise_desc(ValueError, 'No tests found.' , folder=folder)


    mcdplibs = locate_files(folder, '*.mcdplib', include_directories=True,
                            include_files=False)
    n = len(mcdplibs)
    if n <= 1:
        msg = 'Expected more tests.'
        raise_desc(ValueError, msg, folder, mcdplibs=mcdplibs)

    c = context.child('mcdplib')
    for m in mcdplibs:
        short = os.path.splitext(os.path.basename(m))[0]
        short = short.replace('.', '_')
        c2 = c.child(short)
        c2.comp_dynamic(mcdplib_define_tst, mcdplib=m)
        
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

    
def mcdplib_define_tst(context, mcdplib):
    """
        mcdplib: folder
        
        loads the tests in mcdp_tests
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

    from mocdp import logger
    
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

    res = solve_main(**params)
