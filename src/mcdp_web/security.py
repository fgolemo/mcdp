import pyramid
from pyramid.httpexceptions import HTTPFound
from pyramid.security import remember, forget

from mcdp import logger

from .resource_tree import ResourceLogout, ResourceLogin, context_display_in_detail


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
        user = self.user_db[request.authenticated_userid]
        logger.error('forbidden url: %s' % request.url)
        logger.error('forbidden referrer: %s' %request.referrer)
        logger.error('forbidden exception: %s' % request.exception.message)
        logger.error('forbidden result: %s' % request.exception.result)
        request.response.status = 403
        res = {}
        res['request_exception_message'] = request.exception.message
        res['request_exception_result'] = request.exception.result
        # path_qs The path of the request, without host but with query string
        res['came_from'] = request.path_qs[1:]
        res['referrer'] = request.referrer
        res['login_form'] = self.make_relative(request, URL_LOGIN)
        res['url_logout'] = self.make_relative(request, URL_LOGOUT)
        res['root'] =  self.get_root_relative_to_here(request)
        
        if context is not None:
            res['context_detail'] =  context_display_in_detail(context)
            logger.error(res['context_detail'])
        else:
            res['context_detail'] =  'no context provided'
        
        if request.authenticated_userid is not None:
            #res['error'] = ''
            res['user'] = user.dict_for_page()
        else:
            res['error'] = 'You need to login to access this resource.'
            res['user'] = None
        return res


    def login(self, context, request):  # @UnusedVariable
        came_from = request.params.get('came_from', "..")
        message = ''
        error = ''
        if 'form.submitted' in request.params:
            login = request.params['login']
            password = request.params['password']
            
            if not self.user_db.exists(login):
                error = 'Could not find user name "%s".' % login
            else:
                if self.user_db.authenticate(login, password):
                    headers = remember(request, login)
                    logger.info('successfully authenticated user %s' % login)
                    return HTTPFound(location=came_from, headers=headers)
                else:
                    error = 'Password does not match.'
        else: 
            login = None
            
        login_form = self.make_relative(request, URL_LOGIN)
         
        if came_from.startswith('/'):
            came_from = self.make_relative(request, came_from)

        res = dict(
            name='Login',
            message=message,
            error=error,
            login_form=login_form,
            came_from=came_from,
        )
        if login is not None:
            res['login'] = login
        res['root'] =  self.get_root_relative_to_here(request)
        return res

    def logout(self, request):
        headers = forget(request)
        came_from = request.referrer
        return HTTPFound(location=came_from, headers=headers)

def groupfinder(userid, request):  # @UnusedVariable
    from mcdp_web.main import WebApp
    app = WebApp.singleton
    
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

    