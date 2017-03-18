import pyramid
from pyramid.httpexceptions import HTTPFound
from pyramid.security import remember, forget

from mcdp import logger

from .resource_tree import ResourceLogout, ResourceLogin, context_display_in_detail
from .environment import cr2e
from .utils0 import add_std_vars_context
from mcdp_web.environment import Environment


URL_LOGIN = '/login/'
URL_LOGOUT = '/logout'

class AppLogin():
    def config(self, config):
        config.add_view(self.login, context=ResourceLogin, renderer='login.jinja2',
                        permission=pyramid.security.NO_PERMISSION_REQUIRED)

        config.add_view(self.logout, context=ResourceLogout, renderer='logout.jinja2',
                         permission=pyramid.security.NO_PERMISSION_REQUIRED)

        config.add_forbidden_view(self.view_forbidden, renderer='forbidden.jinja2')

    def view_forbidden(self, request):
        # if using as argument, context is the HTTPForbidden exception
        context = request.context
        e = Environment(context, request)
        
        logger.error('forbidden url: %s' % request.url)
        logger.error('forbidden referrer: %s' %request.referrer)
        logger.error('forbidden exception: %s' % request.exception.message)
        logger.error('forbidden result: %s' % request.exception.result)
        request.response.status = 403
        res = {}
        res['request_exception_message'] = request.exception.message
        res['request_exception_result'] = request.exception.result
        # path_qs The path of the request, without host but with query string
        res['came_from'] = request.path_qs
        res['referrer'] = request.referrer
        res['login_form'] = self.make_relative(request, URL_LOGIN)
        res['url_logout'] = self.make_relative(request, URL_LOGOUT)
        res['root'] =   e.root
        res['static'] = e.root + '/static'
        if context is not None:
            res['context_detail'] =  context_display_in_detail(context)
            logger.error(res['context_detail'])
        else:
            res['context_detail'] =  'no context provided'
        
        if e.username is not None:
            #res['error'] = ''
            res['user'] = e.user.dict_for_page()
        else:
            res['error'] = 'You need to login to access this resource.'
            res['user'] = None
        return res

    @add_std_vars_context
    @cr2e
    def login(self, e):  # @UnusedVariable
        came_from = e.request.params.get('came_from', None)
        if came_from is not None:
            logger.info('came_from from params: %s' % came_from)
        else:
            came_from = e.request.referrer
            if came_from is not None:
                logger.info('came_from from referrer: %s' % came_from)
            else:
                msg = 'Cannot get referrer or "came_from" - using root'
                logger.info(msg)
                came_from = self.get_root_relative_to_here(e.request)
        message = ''
        error = ''
        if 'form.submitted' in e.request.params:
            login = e.request.params['login']
            password = e.request.params['password']
            
            if not self.user_db.exists(login):
                error = 'Could not find user name "%s".' % login
            else:
                if self.user_db.authenticate(login, password):
                    headers = remember(e.request, login)
                    logger.info('successfully authenticated user %s' % login)
                    raise HTTPFound(location=came_from, headers=headers)
                else:
                    error = 'Password does not match.'
        else: 
            login = None
            
#         login_form = self.make_relative(e.request, URL_LOGIN)
        
#          
#         if came_from.startswith('/'):
#             came_from = self.make_relative(e.request, came_from)

        res = dict(
            name='Login',
            message=message,
            error=error,
            login_form= e.root + URL_LOGIN,
            came_from=came_from,
        )
        if login is not None:
            res['login'] = login
#         res['root'] =  self.get_root_relative_to_here(e.request)
#         res['static'] = res['root'] + '/static'
        return res

    def logout(self, request):
        headers = forget(request)
        came_from = request.referrer
        if came_from is None:
            came_from = self.get_root_relative_to_here(request)
        raise HTTPFound(location=came_from, headers=headers)

def groupfinder(userid, request):  # @UnusedVariable
    from mcdp_web.main import WebApp
    app = WebApp.singleton
    if not userid in app.user_db:
        msg = 'The user is authenticated as "%s" but no such user in DB.' % userid
        logger.error(msg)
        userid = None # anonymous
    user = app.user_db[userid]
    return ['group:%s' % _ for _ in user.groups]  
# 
# def hash_password(pw):
#     pwhash = bcrypt.hashpw(pw.encode('utf8'), bcrypt.gensalt())
#     return pwhash.decode('utf8')
# 
# def check_password(pw, hashed_pw):
#     expected_hash = hashed_pw.encode('utf8')
#     return bcrypt.checkpw(pw.encode('utf8'), expected_hash)

    