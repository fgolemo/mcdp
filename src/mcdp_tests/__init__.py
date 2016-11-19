# -*- coding: utf-8 -*-

import logging
import numpy
logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def load_tests_modules():
    """ Loads all the mcdp_lang_tests that register using comptests facilities. """

    import mcdp_posets_tests
    import mcdp_lang_tests
    import mcdp_dp_tests
    import mcdp_web_tests
    import mcdp_opt_tests
    import mcdp_figures_tests

    from mocdp.comp.flattening import tests  # @Reimport
    from mocdp.comp import tests  # @Reimport

    import mcdp_report_ndp_tests


def jobs_comptests(context):
    load_tests_modules()

    c2 = context.child('mcdplib')
    from mcdp_library_tests import define_tests_for_mcdplibs
    define_tests_for_mcdplibs(c2)

    c2 = context.child('mcdpweb')
    from mcdp_web_tests.test_md_rendering import define_tests_mcdp_web
    define_tests_mcdp_web(c2)

    from mcdp_lang_tests.examples import define_tests
    define_tests(context)



    # instantiation
    from comptests import jobs_registrar
    from comptests.registrar import jobs_registrar_simple
    jobs_registrar_simple(context)


