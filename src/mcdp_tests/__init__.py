# -*- coding: utf-8 -*-
# Author: Andrea Censi <acensi@idsc.mavt.ethz.ch>
 
import logging
import os

import numpy

from mcdp import MCDPConstants
import warnings

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

def get_test_index():
    """ Returns i,n: machine index and mcdp_comp_tests """
    n = int(os.environ.get('CIRCLE_NODE_TOTAL', 1))
    i = int(os.environ.get('CIRCLE_NODE_INDEX', 0))
    return i, n

def should_do_basic_tests():
    
    # if there is build parallelism
    # only do basic mcdp_comp_tests if we are #0
    i, n = get_test_index()

    #logger.info('Testing box #%d of %d' % (i+1, n))
    if n == 1: # only one total
        should = True
    else: # the first of many
        should = (i == 0)
    
    logger.debug('should_do_basic_tests i = %s n = %d should? %s' % (i, n, should))
    return should

def load_tests_modules():
    """ Loads all the mcdp_lang_tests that register using comptests facilities. """

    if should_do_basic_tests():
        import mcdp_posets_tests
        import mcdp_lang_tests
        import mcdp_dp_tests
        import mcdp_web_tests
        import mcdp_figures_tests
        import mcdp_docs_tests
        import mcdp_report_ndp_tests
        import mcdp_repo_tests
        from mocdp.comp.flattening import tests  # @Reimport
        import mcdp_comp_tests
        import mcdp_hdb_tests
        import mcdp_hdb_mcdp_tests

        vname = MCDPConstants.ENV_TEST_SKIP_MCDPOPT
        if vname in os.environ:
            logger.info('skipping mcdp_opt_tests')
        else:
            if True:
                warnings.warn('removed mcdp_opt_tests for now')
            else:
                import mcdp_opt_tests


def jobs_comptests(context):
    load_tests_modules()

    c2 = context.child('libraries')
    from mcdp_library_tests import define_tests_for_mcdplibs
    define_tests_for_mcdplibs(c2)


    if should_do_basic_tests():
        from mcdp_lang_tests.examples import define_tests
        define_tests(context)

        c2 = context.child('mcdpweb')
        from mcdp_web_tests.test_md_rendering import define_tests_mcdp_web
        define_tests_mcdp_web(c2)

    # instantiation
    from comptests import jobs_registrar
    from comptests.registrar import jobs_registrar_simple
    jobs_registrar_simple(context)
