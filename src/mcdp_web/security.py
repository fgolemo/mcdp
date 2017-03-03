import pyramid
from pyramid.httpexceptions import HTTPFound
from pyramid.security import remember, forget

from mcdp import logger


URL_LOGIN = '/login/'

class AppLogin():
    def config(self, config):
        config.add_route('login', URL_LOGIN)
        config.add_view(self.login, route_name='login', renderer='login.jinja2',
                        permission=pyramid.security.NO_PERMISSION_REQUIRED)

        config.add_route('logout', '/logout')
        config.add_view(self.logout, route_name='logout', renderer='logout.jinja2',
                         permission=pyramid.security.NO_PERMISSION_REQUIRED)

        config.add_forbidden_view(self.view_forbidden, renderer='forbidden.jinja2')

    def view_forbidden(self, request):
        logger.error(request.url)
        logger.error(request.referrer)
        logger.error(request.exception.message)
        logger.error(request.exception.result)
        request.response.status = 403
        res = {}
        res['request_exception_message'] = request.exception.message
        res['request_exception_result'] = request.exception.result
        
        # path_qs The path of the request, without host but with query string
        res['came_from'] = request.path_qs
        res['referrer'] = request.referrer
        res['login_form'] = self.make_relative(request, URL_LOGIN)
        res['root'] =  self.get_root_relative_to_here(request)
        res['message'] = ''
        res['error'] = 'You need to login to access this resource.'
        return res


    def login(self, request): 
        came_from = request.params.get('came_from', '/')
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
# 
# def hash_password(pw):
#     pwhash = bcrypt.hashpw(pw.encode('utf8'), bcrypt.gensalt())
#     return pwhash.decode('utf8')
# 
# def check_password(pw, hashed_pw):
#     expected_hash = hashed_pw.encode('utf8')
#     return bcrypt.checkpw(pw.encode('utf8'), expected_hash)

    