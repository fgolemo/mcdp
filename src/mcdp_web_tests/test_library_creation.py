from comptests.registrar import run_module_tests, comptest
from mcdp_tests import logger
from mcdp_web.main import WebApp
from mcdp_web.resource_tree import ResourceLibrariesNewLibname
from mcdp_web_tests.test_jinja_rendering import with_pyramid_environment

from contracts.utils import check_isinstance
from nose.tools import assert_equal
from pyramid.httpexceptions import HTTPFound

from mcdp_web_tests.mockups import get_context_request


@comptest
@with_pyramid_environment
def test_lib_creation1(env):
    logger.info('env: %s' % env)
    app = WebApp.singleton # XXX
    db_view = app.hi.db_view
    
    authenticated_userid = 'andrea'
    repo_name = 'bundled'
    shelf_name = 'examples'
    library_name = 'newlibname2'
    # check that it doesn't exist
    assert repo_name in db_view.repos
    repo = db_view.repos[repo_name]
    assert shelf_name in repo.shelves
    shelf = repo.shelves[shelf_name]
    if library_name in shelf.libraries:
        msg = 'The library %r already exists' % library_name
        raise Exception(msg)
    
    url = '/repos/%s/shelves/%s/libraries/:new/%s' % (repo_name, shelf_name, library_name)
    
    mocked = get_context_request(test_env=env, url=url, authenticated_userid=authenticated_userid)
    
    context = mocked.context
    request = mocked.request
    check_isinstance(context, ResourceLibrariesNewLibname)
    assert_equal(context.name, library_name)
    # create library
    view = app.view_shelf_library_new 
    try:
        view(context=context, request=request)
    except HTTPFound as e:
        headers=dict(e._headerlist)
        location = headers['Location']
        logger.debug('redirect to: %r' % location)

    else:
        msg = 'Expected HTTPFound raised'
        raise Exception(msg)
    # now the library should exist
    assert library_name in shelf.libraries

if __name__ == '__main__':
    run_module_tests()