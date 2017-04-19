from comptests.registrar import comptest, run_module_tests
from mcdp.logs import logger
from mcdp_utils_misc.my_yaml import yaml_load, yaml_dump


@comptest 
def yaml_representation_of_null():
    none_s = yaml_dump(None)
    logger.info('none is %r' % none_s)
    back = yaml_load(none_s)
    if not back is None:
        raise Exception('%r -> %r, not None' % (none_s, back))
    
    
if __name__ == '__main__':
    run_module_tests()
