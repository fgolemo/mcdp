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
    request = env['request']
    return render_to_response(template, res, request=request)    


@comptest
@with_pyramid_environment
def test_rendering_confirm_bind(env):
    logger.info('env: %s' % env)
    template = get_template('confirm_bind.jinja2')
    res = {
        'static': '',
        'url_edit': '',
        'library_name': '',
        'widget_name': '',
    } 
    request = env['request']
    return render_to_response(template, res, request=request)    

        
if __name__ == '__main__':
    run_module_tests()
