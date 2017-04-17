from collections import namedtuple
import os

from contracts.utils import raise_desc
from mcdp import logger, MCDPConstants
from mcdp_utils_misc.memoize_simple_imp import memoize_simple
from mcdp_library import Librarian
from mcdp_utils_misc.dir_from_package_nam import dir_from_package_name


TestLibrary = namedtuple('TestLibrary', 'bigpath librarian short path ')

@memoize_simple
def get_test_librarian():
    package = dir_from_package_name('mcdp_data')
    folder = os.path.join(package, 'bundled.mcdp_repo')

    if not os.path.exists(folder):
        raise_desc(ValueError, 'Test folders not found.' , folder=folder)

    librarian = Librarian()
    librarian.find_libraries(folder)
    
    libraries = librarian.libraries
    n = len(libraries)
    if n <= 1:
        msg = 'Expected more libraries.'
        raise_desc(ValueError, msg, folder, libraries=libraries)

    orig = list(libraries)
    vname = MCDPConstants.ENV_TEST_LIBRARIES
    
    if vname in os.environ:
        use = os.environ[vname].split(",")
        
        logger.debug('environment variable %s = %s' % (vname, use))
        
        logger.info('Because %s is set, I will use only %s instead of %s.' %
                     (vname, use, orig))
        
        for _ in orig:
            if not _ in use:
                del libraries[_] 
    else:
        logger.debug('environment variable %s is unset' % vname)
        

    vname2 = MCDPConstants.ENV_TEST_LIBRARIES_EXCLUDE
    if vname2 in os.environ:
        exclude = os.environ[vname2].split(',')
        logger.debug('environment variable %s = %s' % (vname2, exclude))
    else:
        exclude = []
        logger.debug('environment variable %s is unset' % vname2)


    if exclude:
        for a in exclude:
            if not a in libraries:
                msg = '%s = %s but %r is not a library.' % (vname2, exclude, a)
                logger.error(msg)
            else:
                logger.info('Excluding %s' % vname2)
                del libraries[a]

    return librarian
