# -*- coding: utf-8 -*-

import logging
from comptests.registrar import jobs_registrar_simple
logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# from .configuration import *
# import mcdp_posets
# from . import dp

import numpy
numpy.seterr('raise')

def load_tests_modules():
    """ Loads all the mcdp_lang_tests that register using comptests facilities. """

    from mcdp_posets import tests
    import mcdp_lang_tests  # @Reimport
    from mcdp_report import tests  # @Reimport

    import mcdp_dp_tests
    # from .example_battery import mcdp_lang_tests  # @Reimport

    from mocdp.comp.flattening import tests  # @Reimport

    from mocdp.comp import tests  # @Reimport


def jobs_comptests(context):
#     from mocdp.configuration import get_conftools_mocdp_config

    # configuration
#     from conf_tools import GlobalConfig
#     GlobalConfig.global_load_dir("mocdp")

    load_tests_modules()

    c2 = context.child('mcdplib')
    from mcdp_library_tests import define_tests_for_mcdplibs
    define_tests_for_mcdplibs(c2)

    from mcdp_lang_tests.examples import define_tests
    define_tests(context)

    # instantiation
    from comptests import jobs_registrar
    jobs_registrar_simple(context)
    # jobs_registrar(context, get_conftools_mocdp_config())


