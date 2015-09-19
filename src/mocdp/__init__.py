from .configuration import *
from .defs import *


def jobs_comptests(context):
    # configuration
    from conf_tools import GlobalConfig
    GlobalConfig.global_load_dir("mocdp.configs")

    # tests
    from . import unittests

    # instantiation
    from comptests import jobs_registrar
    from mocdp.configuration import get_conftools_mocdp_config
    jobs_registrar(context, get_conftools_mocdp_config())
