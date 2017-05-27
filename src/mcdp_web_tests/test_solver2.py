from comptests.registrar import run_module_tests, comptest
from mcdp_tests import logger
from mcdp_web.main import WebApp
from mcdp_web.resource_tree import ResourceThingViewSolver
from mcdp_web_tests.test_jinja_rendering import with_pyramid_environment

from contracts.utils import check_isinstance
from pyramid.httpexceptions import HTTPFound

from mcdp_web_tests.mockups import get_context_request, USER1


@comptest
@with_pyramid_environment
def test_lib_creation1(env):
    logger.info('env: %s' % env)
    app = WebApp.singleton # XXX
    
    authenticated_userid = USER1
    repo_name = 'bundled'
    shelf_name = 'uav_energetics'
    library_name = 'droneA_v1'
    model_name = 'Actuation'
    # check that it doesn't exist
    
    url = ('/repos/%s/shelves/%s/libraries/%s/models/%s/views/solver2/'  % 
           (repo_name, shelf_name, library_name, model_name))
    
    mocked = get_context_request(test_env=env, url=url, authenticated_userid=authenticated_userid)
    
    context = mocked.context
    request = mocked.request
    check_isinstance(context, ResourceThingViewSolver)
    
    # create library
    view = app.view_solver2_base
    try: 
        view(context=context, request=request)
    except HTTPFound as e:
        headers=dict(e._headerlist)
        location = headers['Location']
        logger.debug('original url: %s' % request.url)
        logger.debug('redirect to: %r' % location)
        
    url2 = url + 'submit'
    ui_state = {} 
    checkboxes = ['ftor_checkbox', 'rtof_checkbox', 'solveforx_checkbox',
'frtoi_checkbox', 'existsi_checkbox', 'itofr_checkbox']
    ui_state['area_F'] = '2.0 N'
    ui_state['area_R'] = ''
    for c in checkboxes:
        ui_state[c] = False
    ui_state['ftor_checkbox'] = True
    ui_state['do_approximations'] = False 
    
    ui_state['nu'] = 10
    ui_state['nl'] = 11

    json_body = {'ui_state': ui_state}
    
    mocked2 = get_context_request(test_env=env, url=url2, authenticated_userid=authenticated_userid,
                                  referrer=url, json_body=json_body)
    view = app.view_solver2_submit
    
    res = view(context=mocked2.context, request=mocked2.request)
    
    #print res
    if app.exceptions:
        msg = 'Found these exceptions:'
        msg += '\n'.join(app.exceptions)
        raise Exception(msg)
    
    assert isinstance(res, dict)
    assert 'ok' in res
    assert res['ok']
    assert '12 W' in res['output_result']
    
    
    # now do the other way
    
    ui_state['ftor_checkbox'] = False # disable old
    ui_state['rtof_checkbox'] = True
    ui_state['area_R'] = '12 W'
    
    res2 = view(context=mocked2.context, request=mocked2.request)
    print res2
    if app.exceptions:
        msg = 'Found these exceptions:'
        msg += '\n'.join(app.exceptions)
        raise Exception(msg)


    assert isinstance(res2, dict)
    assert 'ok' in res2
    assert res2['ok']
    assert '2 N' in res2['output_result']
    
if __name__ == '__main__':
    run_module_tests()
    