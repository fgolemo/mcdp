from collections import namedtuple
import os

from contracts.utils import raise_desc
from mcdp import logger, MCDPConstants
from mcdp_utils_misc import memoize_simple
from mcdp_library import Librarian
from mcdp_utils_misc import dir_from_package_name



TestLibrary = namedtuple('TestLibrary', 'bigpath librarian short path ')

@memoize_simple
def get_test_db():
    ''' Returns the db_view for the test data '''
    from mcdp_hdb_mcdp.main_db_schema import DB
    from mcdp_hdb.pipes import mount_directory
#     from mcdp_hdb.disk_struct import ProxyDirectory
    disk_map = DB.dm
    # first generate test db
    db_schema = DB.db
    db_data = db_schema.generate_empty()
    db_view = DB.view_manager.create_view_instance(db_schema, db_data)
    
    package = dir_from_package_name('mcdp_data')
    dirname = os.path.join(package, 'bundled.mcdp_repo')
    # read repo from dirname
#     d = ProxyDirectory.from_disk(dirname)
#     bundled = disk_map.interpret_hierarchy_(DB.repo, d)
    
#     shelf_unittests = bundled
    repo_name = 'bundled'
    # create one 
    
    mount_directory(view0=db_view.repos, child_name=repo_name, disk_map=disk_map, dirname=dirname)
    return db_view
    
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
        pass
        #logger.debug('environment variable %s is unset' % vname)

    vname2 = MCDPConstants.ENV_TEST_LIBRARIES_EXCLUDE
    if vname2 in os.environ:
        exclude = os.environ[vname2].split(',')
        logger.debug('environment variable %s = %s' % (vname2, exclude))
    else:
        exclude = []
        # logger.debug('environment variable %s is unset' % vname2)


    if exclude:
        for a in exclude:
            if not a in libraries:
                msg = '%s = %s but %r is not a library.' % (vname2, exclude, a)
                logger.error(msg)
            else:
                logger.info('Excluding %s' % vname2)
                del libraries[a]

    return librarian
