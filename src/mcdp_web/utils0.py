# -*- coding: utf-8 -*-
import traceback
import urlparse

from contracts.utils import check_isinstance, indent, raise_desc
from pyramid.httpexceptions import HTTPException, HTTPFound
from pyramid.response import Response
from pyramid.security import forget

from mcdp import MCDPConstants, logger, __version__
from mcdp_utils_misc import duration_compact,  format_list
from mcdp_user_db.user import UserInfo, User 
from contracts import contract


Privileges = MCDPConstants.Privileges


def add_other_fields(self, res, request, context):
    from .environment import Environment
    from .get_navigation_links_imp import get_navigation_links_context

    e = Environment(context, request)
    res['navigation'] = get_navigation_links_context(e)
    res['navigation'].update(e.__dict__)
    res['version'] = lambda: __version__
    res['root'] = self.get_root_relative_to_here(request)

    def _has_library_doc(document):
        return document in e.library.documents 

    # template functions
    res['render_library_doc'] = lambda docname: self._render_library_doc(
        request, docname)
    res['has_library_doc'] = _has_library_doc
    res['uptime_s'] = int(self.get_uptime_s())
    res['uptime_string'] = duration_compact(res['uptime_s'])
    res['time_start'] = self.time_start
    res['authenticated_userid'] = request.authenticated_userid

    session = self.get_session(request) 
    
    if e.username is not None:
        res['user_info'] = e.user_info
        res['user_struct'] = e.user_struct
    else:
        res['user_info'] = None 
        res['user_struct'] = None
        
    app = self
    res['user_db'] = app.hi.db_view.user_db
    
    def shelf_privilege(repo_name, sname, privilege):
        repos = session.app.hi.db_view.repos
        repo = repos[repo_name]
        if not sname in repo.shelves:
            msg = 'Cannot find shelf "%s" in repo "%s".' % (sname, repo_name)
            msg += '\n available: ' + format_list(repo.shelves)
            raise ValueError(msg)
        acl = repo.shelves[sname].get_acl()
        return acl.allowed2(privilege, e.user_info)

    def can_subscribe(repo_name, sname):
        return shelf_privilege(repo_name, sname, Privileges.SUBSCRIBE)

    def can_read(repo_name, sname):
        return shelf_privilege(repo_name, sname, Privileges.READ)

    def can_write(repo_name, sname):
        return shelf_privilege(repo_name, sname, Privileges.WRITE)

    def can_admin(repo_name, sname):
        return shelf_privilege(repo_name, sname, Privileges.ADMIN)

    def can_discover(repo_name, sname):
        return shelf_privilege(repo_name, sname, Privileges.DISCOVER)

    def shelf_subscribed(repo_name, _):  # @UnusedVariable
        return _ in e.user_info.subscriptions
    
    res['shelf_can_read'] = can_read
    res['shelf_can_write'] = can_write 
    res['shelf_can_subscribe'] = can_subscribe
    res['shelf_can_discover'] = can_discover
    res['shelf_can_admin'] = can_admin
    res['shelf_subscribed'] = shelf_subscribed

    def library_url(_):
        if _ is None:
            msg = 'library_name = None'
            raise ValueError(msg)
        if e.shelf_name is None:
            msg = 'shelf_name is not set'
            raise ValueError(msg)
        url = '{root}/repos/{repo_name}/shelves/{shelf_name}/libraries/{this}'
        return url.format(this=_, **e.__dict__)

    def library_url2(repo_name, shelf_name, library_name): 
        url = '{root}/repos/{repo_name}/shelves/{shelf_name}/libraries/{library_name}'
        return url.format(root=e.root,  repo_name=repo_name, shelf_name=shelf_name, library_name=library_name)

    def thing_url(t):
        url = '{root}/repos/{repo_name}/shelves/{shelf_name}/libraries/{library_name}/{spec_name}/%s' % t
        return url.format(**e.__dict__)

    res['thing_url'] = thing_url

    res['library_url'] = library_url
    res['library_url2'] = library_url2

    def repo_url(repo_name):
        return e.root + '/repos/' + repo_name

    def shelf_url(repo_name, shelf_name):
        return e.root + '/repos/' + repo_name + '/shelves/' + shelf_name
    res['repo_url'] = repo_url

    res['shelf_url'] = shelf_url
    res['static'] = e.root + '/static'

    res['icon_repo'] = '&#9730;'
    res['icon_repo_css'] = r'\9730;'
    res['icon_library'] = '&#x1F4D6;'
    res['icon_library_css'] = r'\1F4D6'
    res['icon_shelf'] = '&#x1F3DB;'
    res['icon_shelf_css'] = r'\1F3DB'

    res['icon_models'] = '&#10213;'
    res['icon_templates'] = '&#x2661;'
    res['icon_posets'] = '&#x28B6;'
    res['icon_values'] = '&#x2723;'
    res['icon_primitivedps'] = '&#x2712;'

    res['icon_documents'] = '&#128196;'
    
    providers = self.get_authomatic_config()
    other_logins = {}
    for x in providers:
        other_logins[x] = e.root + '/authomatic/' + x
    res['other_logins'] = other_logins

    def icon_spec(spec_name):
        return res['icon_%s' % spec_name]
    res['icon_spec'] = icon_spec

#     def get_user(username):
#         x = session.get_user_struct(username)
#         return x.info.dict_for_page()
    def get_userstruct(username):
        return session.get_user_struct(username)
   
    res['get_userstruct'] = get_userstruct

    add_jinja_tests(res)
    
def add_jinja_tests(res):

    @contract(a_user=User)    
    def is_current_user(a_user):
        ''' return true if this is the current user '''
        x = res['authenticated_userid']
        return x and (x == a_user.info.username)
    
    @contract(ui=UserInfo)    
    def is_current_user_ui(ui):
        ''' return true if this is the current user '''
#         the_user = res['user_struct']
        x = res['authenticated_userid']
        return x and (x ==  ui.username)

    res['is_current_user_ui'] = is_current_user_ui
    res['is_current_user'] = is_current_user
    
    def is_userstruct(what):
        return isinstance(what, User) #and what._schema == DB.user
    def is_userinfo(what):
        return isinstance(what, UserInfo)
    def assert_is_string(what):
        check_isinstance(what, str)
        return ''
    def assert_is_userstruct(what):
        if is_userinfo(what):
            msg = 'This is a UserInfo, not a UserStruct'
            raise Exception(msg)
        check_isinstance(what, User)
        return ''
    def assert_is_userinfo(what):
        if is_userstruct(what):
            msg = 'This is a UserStruct, not a UserInfo'
            raise Exception(msg) 
        check_isinstance(what, UserInfo)
        return ''
    res['assert_is_string'] = assert_is_string
    res['assert_is_userstruct'] = assert_is_userstruct
    res['assert_is_userinfo'] = assert_is_userinfo
    
def add_std_vars_context(f):
    return add_std_vars_context_(f, redir=True)

def add_std_vars_context_no_redir(f):
    return add_std_vars_context_(f, redir=False)

def add_std_vars_context_(f, redir):
    from .resource_tree import context_display_in_detail, Resource

    def f0(self, context, request):
        url_base_internal = self.options.url_base_internal
        if url_base_internal is not None:
            if not request.url.startswith(url_base_internal):
                msg = ('Given that url_base_internal is set, I was expecting that all urls'
                       ' would start with it.')
                raise_desc(Exception, msg, 
                           request_url=request.url, 
                           url_base_internal=url_base_internal)
                
        if '//' in urlparse.urlparse(request.url).path:
            msg = 'This is an invalid URL with 2 slashes: %s' % request.url
            response = Response(msg)
            response.status_int = 500
            return response
        
        if redir:
            url = request.url
            p = urlparse.urlparse(url)
            url2 = url
            # only do redirection if we have url_base_internal
            # The redirection is needed because of https; however
            # for casual use it is likely https is not set up.
            if self.options.url_base_internal:
                if '127.0.0.1' in p.netloc:
                    url2 = url2.replace('127.0.0.1', 'localhost')
            if not p.path.endswith('.html'):
                if not p.path.endswith('/'):
                    url2 = url2.replace(p.path, p.path + '/')
            
            if url2 != url:
                logger.info('Context: %s' % context)
                logger.info('Redirection:\n from: %s\n   to: %s' % (url, url2))
                raise HTTPFound(url2)

            if request.authenticated_userid:
                uid = request.authenticated_userid
                from mcdp_web.main import WebApp
                app = WebApp.singleton
                user_db = app.hi.db_view.user_db
                if not uid in user_db:
                    msg = 'The user is authenticated as "%s" but no such user in DB.' % uid
                    msg += 'We are logging out the user.'
                    logger.warn(msg)
                    headers = forget(request)
                    raise HTTPFound(location=request.url, headers=headers)
 
        try:
            res = f(self, context, request)
        except HTTPException:
            raise
        except Exception as e:
            msg = 'While running %s:' % (f.__name__)
            msg += '\n' + indent(traceback.format_exc(e), ' >')
            logger.error(msg)
            raise
        if isinstance(res, Response):
            return res
        check_isinstance(res, dict)
        try:
            add_other_fields(self, res, request, context=context)
        except:
            logger.error('Error after executing view %s' % f)
            if isinstance(context, Resource):
                logger.debug(context_display_in_detail(context))
            raise
        return res
    return f0
