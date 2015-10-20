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
        
def test_one(test, filename):
    with open(filename) as f:
        contents = f.read()
    test(contents)

def test_report_dp1(filename, outdir, basename):
    from mocdp.lang.syntax import parse_ndp
    with open(filename) as f:
        contents = f.read()
    ndp = parse_ndp(contents)
    dp = ndp.get_dp()
    from mocdp.dp_report.report import report_dp1
    r = report_dp1(dp)
    f = os.path.join(outdir, '%s_dp1.html' % basename)
    r.to_html(f)
    print('Written to %r.' % f)
    return r

def test_report_ndp1(filename, outdir, basename):
    from mocdp.lang.syntax import parse_ndp
    with open(filename) as f:
        contents = f.read()
    ndp = parse_ndp(contents)
    from mocdp.dp_report.report import report_ndp1
    r = report_ndp1(ndp)
    f = os.path.join(outdir, '%s_ndp1.html' % basename)
    r.to_html(f)
    print('Written to %r.' % f)
    return r

def define_test_for(context, filename, basename):
    outdir = os.path.dirname(filename)
    outdir = os.path.join(outdir, 'out')

    tests = get_marked_tests(filename)
    print('tests for %s: %s' % (filename , tests))
    
    for test in tests:
        n = test.__name__.replace('assert_', '').replace('_ndp', '')
        p_job_id = '%s-%s' % (basename, n)
        p_job = context.comp_config(test_one, test, filename,
                                    job_id=p_job_id)
        
    if assert_parsable_to_unconnected_ndp in tests:
        job_id = '%s-%s' % (basename, 'report_ndp1')
        r = context.comp_config(test_report_ndp1, filename, outdir, basename,
                                job_id=job_id, extra_dep=[p_job])
        context.add_report(r, 'examples_report_ndp1', file=basename)
        
    if assert_parsable_to_connected_ndp in tests or assert_parsable_to_connected_ndp in tests:
        job_id = '%s-%s' % (basename, 'report_dp1')
        r = context.comp_config(test_report_dp1, filename, outdir, basename,
                                 job_id=job_id, extra_dep=[p_job])
        context.add_report(r, 'examples_report_dp1', file=basename)
        
    
def define_tests(context):
    folder = dir_from_package_name('mocdp.lang.tests.ok')

    filenames = locate_files(folder, '*.cdp')

    context = context.child('examples')
    for f in filenames:
        basename = os.path.splitext(os.path.basename(f))[0]
        define_test_for(context, f, basename)
