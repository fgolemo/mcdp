from contextlib import contextmanager
import os

from pyramid.paster import bootstrap
from pyramid.renderers import render_to_response

from comptests.registrar import run_module_tests, comptest
from mcdp_tests import logger
from mcdp_utils_misc import dir_from_package_name


def with_pyramid_environment(f):
    @contextmanager
    def f2():
        d = dir_from_package_name('mcdp_web_tests')
        ini = os.path.join(d, 'test1.ini')
        with bootstrap(ini) as env:
            f(env)
        
    f2.__name__ = f.__name__
    return f2

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


@comptest
@with_pyramid_environment
def test_rendering_confirm_bind_bind(env):
    logger.info('env: %s' % env)
    template = get_template('confirm_bind_bind.jinja2')
    res = {
        'static': '',
    } 
    check_render(env, template, res)  

@comptest
@with_pyramid_environment
def test_rendering_confirm_creation_similar(env):
    logger.info('env: %s' % env)
    template = get_template('confirm_creation_similar.jinja2')
    res = {
        'static': '',
    } 
    check_render(env, template, res) 

@comptest
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
    res = {
        'static': '', 
    } 
    check_render(env, template, res)    

        
if __name__ == '__main__':
    run_module_tests()
