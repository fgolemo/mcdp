from comptests.registrar import register_indep
from conf_tools.utils.locate_files_imp import locate_files
from conf_tools.utils.resources import dir_from_package_name
from contracts.utils import raise_desc
from mocdp.lang.tests.utils import (assert_parsable_to_connected_ndp,
    assert_parsable_to_unconnected_ndp, assert_semantic_error,
    assert_syntax_error)
import os

def get_marked_tests(filename):
    with open(filename) as f:
        contents = f.read()

    line1 = contents.split('\n')[0]
    if not 'test' in line1:
        msg = 'Please add a "test" comment at the beginning of the file.'
        raise_desc(Exception, msg, line1=line1, filename=filename)

    tests = []
    if 'unconnected' in line1:
        tests.append(assert_parsable_to_unconnected_ndp)
    elif 'connected' in line1:
        tests.append(assert_parsable_to_connected_ndp)
    elif 'semantic_error' in line1:
        tests.append(assert_semantic_error)
    elif 'syntax_error' in line1:
        tests.append(assert_syntax_error)
    else:
        msg = 'Please add one of "connected", "unconnected", '
        msg += '"semantic_error", "syntax_error" at the beginning of the file.'
        raise_desc(Exception, msg, line1=line1, filename=filename)
    return tests
#
# def test_one(filename):
#     with open(filename) as f:
#         contents = f.read()
#
#     line1 = contents.split('\n')[0]
#     if not 'test' in line1:
#         msg = 'Please add a "test" comment at the beginning of the file.'
#         raise_desc(Exception, msg, line1=line1, filename=filename)
#
#
#     if 'unconnected' in line1:
#         assert_parsable_to_unconnected_ndp(contents)
#     elif 'connected' in line1:
#         assert_parsable_to_connected_ndp(contents)
#     elif 'semantic_error' in line1:
#         assert_semantic_error(contents)
#     elif 'syntax_error' in line1:
#         assert_syntax_error(contents)
#     else:
#         msg = 'Please add one of "connected", "unconnected", '
#         msg += '"semantic_error", "syntax_error" at the beginning of the file.'
#         raise_desc(Exception, msg, line1=line1, filename=filename)
        
def test_one(test, filename):
    with open(filename) as f:
        contents = f.read()
    test(contents)

def define_test_for(filename, basename):

    tests = get_marked_tests(filename)
    for test in tests:
        job_id = 'file-%s-%s' % (basename, test.__name__)
        register_indep(test_one, dynamic=False, args=(test, filename,),
                    kwargs=dict(job_id=job_id))
    
def define_tests():
    folder = dir_from_package_name('mocdp.lang.tests.ok')

    filenames = locate_files(folder, '*.cdp')

    for f in filenames:
        basename = os.path.splitext(os.path.basename(f))[0]
        define_test_for(f, basename)
