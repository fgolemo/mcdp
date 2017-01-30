import os

import pyramid
from pyramid.httpexceptions import HTTPFound
from pyramid.security import remember, forget

from mocdp import logger


USERS = {}

GROUPS = {'editor': ['group:editors']}

def load_users(userdir):
    if not os.path.exists(userdir):
        msg = 'Directory %s does not exist' % userdir
        Exception(msg)
    for user in os.listdir(userdir):
        password = os.path.join(userdir, user, 'password')
        if not os.path.exists(password):
            msg = 'Password file %s does not exist.'  % password
            raise Exception(msg)
        password = open(password).read().strip()
        USERS[user] = password
    print USERS
        
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
        
        load_users(self.options.users)
        
    def view_forbidden(self, request):
        logger.error(request.url)
        logger.error(request.referrer)
        logger.error(request.exception.message)
        logger.error(request.exception.result)
        request.response.status = 403
        res = {}
        res['message'] = request.exception.message
        res['result'] = request.exception.result
        res['url'] = request.url
        res['referrer'] = request.referrer
        res['login_form'] = self.make_relative(request, URL_LOGIN)
        return res


    def login(self, request): 
#         login_url = request.route_url('login')
        referrer = request.url
#         if referrer == login_url:
#             referrer = '/'  # never use login form itself as came_from
        came_from = request.params.get('came_from', referrer)
        message = ''
        login = ''
        password = ''
        if 'form.submitted' in request.params:
            login = request.params['login']
            password = request.params['password']
            if not login in USERS:
                message = 'Could not find user name "%s".' % login
            else:
                password_expected = USERS.get(login)
                #if check_password(password, hashed):
                if password == password_expected:
                    headers = remember(request, login)
                    logger.info('successfully authenticated user %s' % login)
                    return HTTPFound(location=came_from, headers=headers)
                else:
                    message = 'Password does not match.'
            
        login_form = self.make_relative(request, URL_LOGIN)
        print('login_form: %s' % login_form)
        return dict(
            name='Login',
            message=message,
            login_form=login_form,
            came_from=came_from,
            login=login,
            password=password,
        )

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




def groupfinder(userid, request):  # @UnusedVariable
    if userid in USERS:
        return GROUPS.get(userid, [])
    
    