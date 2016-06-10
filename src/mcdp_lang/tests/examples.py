from StringIO import StringIO
from conf_tools.utils import dir_from_package_name, locate_files
from contracts.utils import raise_desc
from mcdp_lang import parse_ndp_filename
from mcdp_lang.tests.utils import (assert_parsable_to_connected_ndp_fn,
    assert_parsable_to_unconnected_ndp_fn, assert_semantic_error_fn,
    assert_syntax_error_fn)
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
        tests.append(assert_parsable_to_unconnected_ndp_fn)
        tests.append(syntax_test_fn)
    elif 'connected' in line1:
        tests.append(assert_parsable_to_connected_ndp_fn)
        tests.append(syntax_test_fn)
    elif 'semantic_error' in line1:
        tests.append(assert_semantic_error_fn)
    elif 'syntax_error' in line1:
        tests.append(assert_syntax_error_fn)
    else:
        msg = 'Please add one of "connected", "unconnected", '
        msg += '"semantic_error", "syntax_error" at the beginning of the file.'
        raise_desc(Exception, msg, line1=line1, filename=filename)
    return tests

def syntax_test_fn(filename):
    with open(filename) as f:
        contents = f.read()
    return syntax_test(contents)

def syntax_test(contents):
    from mcdp_report.html import ast_to_html
    html = ast_to_html(contents, complete_document=False)

    import xml.etree.ElementTree as ETree
    try:
        s = StringIO(html)
        _doc = ETree.parse(s)
    except ETree.ParseError :
        print("ERROR in {0} : {1}".format(ETree.ParseError.filename, ETree.ParseError.msg))


def test_one(test, filename):
    test(filename)


def test_report_dp1(filename, outdir, basename):

    ndp = parse_ndp_filename(filename)
    dp = ndp.get_dp()
    from mcdp_report.report import report_dp1
    r = report_dp1(dp)
    f = os.path.join(outdir, '%s_dp1.html' % basename)
    r.to_html(f)
    print('Written to %r.' % f)
    return r

def test_report_ndp1(filename, outdir, basename):
    ndp = parse_ndp_filename(filename)
    from mcdp_report.report import report_ndp1
    r = report_ndp1(ndp)
    f = os.path.join(outdir, '%s_ndp1.html' % basename)
    r.to_html(f)
    print('Written to %r.' % f)
    return r

def known_fail(f, *args):
    try:
        f(*args)
    except:
        pass
    else:
        msg = 'Should be a known failure.'
        raise Exception(msg)


def define_test_for(context, filename, basename, tests, known_failure=False):

    mocdp_base = dir_from_package_name('mocdp')
    outdir = os.path.join(mocdp_base, '../../out/tests/')
    
    for test in tests:
        n = test.__name__.replace('assert_', '').replace('_ndp', '')
        p_job_id = '%s-%s' % (basename, n)
        
        if not known_failure:
            p_job = context.comp_config(test_one, test, filename,
                                        job_id=p_job_id)
        else:
            context.comp_config(known_fail, test_one, test, filename,
                                job_id=p_job_id)

    if not known_failure:
        if (assert_parsable_to_connected_ndp_fn in tests
            or assert_parsable_to_unconnected_ndp_fn in tests):
            job_id = '%s-%s' % (basename, 'report_ndp1')
            r = context.comp_config(test_report_ndp1, filename, outdir, basename,
                                    job_id=job_id, extra_dep=[p_job])
            context.add_report(r, 'examples_report_ndp1', file=basename)

        if assert_parsable_to_connected_ndp_fn in tests:
            job_id = '%s-%s' % (basename, 'report_dp1')
            r = context.comp_config(test_report_dp1, filename, outdir, basename,
                                     job_id=job_id, extra_dep=[p_job])
            context.add_report(r, 'examples_report_dp1', file=basename)
        
    
def define_tests(context):
    """ Define other tests """
    filenames = []
    folder = dir_from_package_name('mcdp_lang.tests.ok')
    filenames.extend(locate_files(folder, '*.mcdp'))

    context = context.child('examples')
    found = set()
    def get_unique_basename(f):
        orig = os.path.splitext(os.path.basename(f))[0]
        if orig in found:
            for i in range(10):
                bn = '%s_%d' % (orig, i + 1)
                if not bn in found:
                    return bn
            assert False, (orig, found)
        else:
            found.add(orig)
            return orig

    folder = os.path.join(dir_from_package_name('mocdp'), '../../examples')
    examples2 = list(locate_files(folder, '*.mcdp'))
    print('Other files found: %s' % examples2)
    filenames.extend(examples2)

    for f in filenames:

        basename = get_unique_basename(f)
        print('defining %s' % basename)
        if f in examples2:
            contents = open(f).read()
            if '...' in contents:
                tests = [assert_semantic_error_fn]
            else:
                tests = [assert_parsable_to_connected_ndp_fn]
        else:
            tests = get_marked_tests(f)
        define_test_for(context, f, basename, tests)


    folder_notok = 'mcdp_lang.tests.ok'
    filenames = []
    filenames.extend(locate_files(folder_notok, '*.mcdp'))

    context = context.child('notok')
    for f in filenames:
        basename = os.path.splitext(os.path.basename(f))[0]
        tests = get_marked_tests(f)
        define_test_for(context, f, basename, tests, known_failure=True)


