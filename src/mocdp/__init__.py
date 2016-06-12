# -*- coding: utf-8 -*-
__version__ = '1.2.0'

import logging
logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

from .configuration import *
import mcdp_posets
# from . import dp

import numpy
numpy.seterr('raise')

def load_tests_modules():
    """ Loads all the tests that register using comptests facilities. """
    from . import unittests

    from mcdp_posets import tests
    from mcdp_lang import tests  # @Reimport
    from mcdp_report import tests  # @Reimport

    from .dp import tests  # @Reimport
    # from .example_battery import tests  # @Reimport

    from .comp.flattening import tests  # @Reimport

    from .comp import tests  # @Reimport


def jobs_comptests(context):
    # configuration
    from conf_tools import GlobalConfig
    GlobalConfig.global_load_dir("mocdp")

    load_tests_modules()

    c2 = context.child('mcdplib')
    from mcdp_library import define_tests_for_mcdplibs
    define_tests_for_mcdplibs(c2)

    from mcdp_lang.tests.examples import define_tests
    define_tests(context)

    # instantiation
    from comptests import jobs_registrar
    jobs_registrar(context, get_conftools_mocdp_config())


