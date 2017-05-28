from comptests.registrar import run_module_tests, comptest, comptest_fails
from contextlib import contextmanager
from mcdp_hdb_mcdp.main_db_schema import DB
from mcdp_hdb_mcdp_tests.dbs import testdb1
from mcdp_tests import logger
from mcdp_utils_misc import dir_from_package_name
from mcdp_web.main import WebApp
from mcdp_web.utils0 import add_jinja_tests
import os

from pyramid.paster import bootstrap
from pyramid.renderers import render_to_response
from .mockups import with_pyramid_environment
from mcdp_web_tests.mockups import USER1


def get_template(name):
    ''' returns the jinja file  with base in mcdp_web '''
    d = dir_from_package_name('mcdp_web')
    fn = os.path.join(d, name)
    if not os.path.exists(fn):
        msg = 'The template %r does not exist.' % name
        raise ValueError(msg)
    return fn

def check_render(env, template, res):
    ''' Tries to render, and then checks if all parameters are necessary. '''
    request = env['request']
    add_jinja_tests(res)
    
    # first try to render normally
    render_to_response(template, res, request=request)
#     # Then try to see if other params are necessary
#     for k in res:
#         res2 = dict(**res)
#         del res2[k]
#         try:
#             render_to_response(template, res, request=request)
#         except:
#             pass
#         else:
#             msg = 'I expect that removing the parameter %r would make %r fail.' % (k, template)
#             raise Exception(msg)


@comptest
@with_pyramid_environment
def test_rendering_jinja_env(env):
    logger.info('env: %s' % env)
    template = get_template('editor_fancy/error_model_exists_generic.jinja2')
    res = {
        'static': '',
        'url_edit': '',
        'library_name': '',
        'widget_name': '',
    } 
    check_render(env, template, res)


@comptest_fails
@with_pyramid_environment
def test_rendering_confirm_bind_bind(env):
    logger.info('env: %s' % env)
    template = get_template('confirm_bind_bind.jinja2')
    res = {
        'static': '',
    } 
    check_render(env, template, res)  

@comptest_fails
@with_pyramid_environment
def test_rendering_confirm_creation_similar(env):
    logger.info('env: %s' % env)
    template = get_template('confirm_creation_similar.jinja2')
    res = {
        'static': '',
    } 
    check_render(env, template, res) 

@comptest_fails
@with_pyramid_environment
def test_rendering_confirm_creation(env):
    logger.info('env: %s' % env)
    template = get_template('confirm_creation.jinja2')
    res = {
        'static': '',
    } 
    check_render(env, template, res) 
    

@comptest
@with_pyramid_environment
def test_rendering_confirm_bind(env):
    logger.info('env: %s' % env)
    template = get_template('confirm_bind.jinja2')
    app = WebApp.singleton # XXX
    db_view = app.hi.db_view
    uname = USER1
    user = db_view.user_db.users[uname]
    res = {
        'authenticated_userid': 'paul',
        'static': '', 
        'root': '',
        'user_struct': user,
        'candidate_user': user,
        'user_db' : db_view.user_db,
    } 
    check_render(env, template, res)    

        
if __name__ == '__main__':
    run_module_tests()
