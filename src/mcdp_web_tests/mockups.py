from collections import namedtuple
from contextlib import contextmanager
from contracts import contract
from mcdp_hdb_mcdp.main_db_schema import DB
from mcdp_hdb_mcdp_tests.dbs import testdb1
from mcdp_tests import logger
from mcdp_utils_misc import dir_from_package_name
from mcdp_web.main import WebApp
from mcdp_web.resource_tree import MCDPResourceRoot, context_display_in_detail
import os

from pyramid.paster import bootstrap


USER1 = 'uname1'

def with_pyramid_environment(f):
    @contextmanager
    def f2():
        d = dir_from_package_name('mcdp_web_tests')
        ini = os.path.join(d, 'test1.ini')
        with bootstrap(ini) as env:
            app = WebApp.singleton
            db_view0 = app.hi.db_view
            # create a copy of the DB
            db_data0 = db_view0._data
            db_view1 = DB.view_manager.create_view_instance(DB.db, db_data0)
            db_view1.set_root()
            logger.info('creating copies of the repositories')
            for r in db_view0.repos:
                db_view1.repos[r] = db_view0.repos[r]
            logger.info('creating copies of the repositories [done]')

            app.hi.db_view = db_view1
            db0 = testdb1()
            db_view1.user_db.users['anonymous'] = db_view0.user_db.users['anonymous']
            db_view1.user_db.users[USER1] = db0['user_db']['users']['andrea']
            f(env)

    f2.__name__ = f.__name__
    f2.__module__ = f.__module__ # for run_module_tests()
    return f2



class SessionMockup():
    def get_csrf_token(self):
        return 'csrf_token'

class RequestMockup(object):
    def __init__(self, authenticated_userid, url, referrer, json_body):
        self.session = SessionMockup()
        self.authenticated_userid = authenticated_userid
        self.url = url
        self.domain = 'domain'
        self.referrer = referrer
        self.json_body = json_body
        
def get_context_from_url(root, url):
    pieces = url.split('/')
    # remove empty
    pieces = [_ for _ in pieces if _]
    current = root
    while pieces:
        first = pieces.pop(0)
        current = current[first]
        logger.debug('resolving %r -> %s '% (first, type(current).__name__))
        
    logger.debug('\n'+context_display_in_detail(current))
    return current

ContextRequest = namedtuple('ContextRequest', 'context request')

@contract(returns=ContextRequest)
def get_context_request(test_env, url, authenticated_userid=None, referrer=None,
                        json_body=None):  # @UnusedVariable
    assert url.startswith('/')
    url_base_internal = "http://localhost:8080" # XXX: use whatever is in the configuration
    url_all = url_base_internal + url
    request = RequestMockup(authenticated_userid=authenticated_userid, url=url_all, referrer=referrer,
                            json_body=json_body) 
    root = MCDPResourceRoot(request)
    context = get_context_from_url(root, url)
    return ContextRequest(context=context, request=request)
    
    