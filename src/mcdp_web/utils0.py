# -*- coding: utf-8 -*-
import traceback

from contracts.utils import check_isinstance, indent
from pyramid.httpexceptions import HTTPException, HTTPFound

from mcdp import MCDPConstants,  logger, __version__
from mcdp_shelf import PRIVILEGE_SUBSCRIBE, PRIVILEGE_READ, PRIVILEGE_WRITE, PRIVILEGE_ADMIN
from mcdp_utils_misc import duration_compact,  format_list
import urlparse
from pyramid.response import Response


def add_other_fields(self, res, request, context):
    from .environment import Environment
    from .get_navigation_links_imp import get_navigation_links_context


    e = Environment(context, request)
    res['navigation'] = get_navigation_links_context(e)   
    res['navigation'].update(e.__dict__)         
    res['version'] = lambda: __version__ 
    res['root'] = self.get_root_relative_to_here(request)
    
    def _has_library_doc(document):
        filename = '%s.%s' % (document, MCDPConstants.ext_doc_md)
        return e.library.file_exists(filename)
    
    # template functions
    res['render_library_doc'] = lambda docname: self._render_library_doc(request, docname)
    res['has_library_doc'] = _has_library_doc
    res['uptime_s'] = int(self.get_uptime_s())
    res['uptime_string'] = duration_compact(res['uptime_s'])
    res['time_start'] = self.time_start
    res['authenticated_userid'] = request.authenticated_userid
    
    session = self.get_session(request)
    
    user = self.user_db[request.authenticated_userid]
    
    if request.authenticated_userid is not None:
        res['user'] = user.dict_for_page()
    else:
        res['user'] = None
    
    def shelf_privilege(repo_name, sname, privilege):
        repo = session.repos[repo_name]
        if not sname in repo.shelves:
            msg = 'Cannot find shelf "%s" in repo "%s".' % (repo_name, sname)
            msg += '\n get_all_available_plotters: ' + format_list(repo.shelves)
            raise ValueError(msg) 
        acl = repo.shelves[sname].get_acl()
        return acl.allowed2(privilege, user)
         
    def can_subscribe(repo_name, sname):
        return shelf_privilege(repo_name, sname, PRIVILEGE_SUBSCRIBE)
    
    def can_read(repo_name, sname):
        return shelf_privilege(repo_name,sname, PRIVILEGE_READ)
    
    def can_write(repo_name, sname):
        return shelf_privilege(repo_name, sname, PRIVILEGE_WRITE)
    
    def can_admin(repo_name, sname):
        return shelf_privilege(repo_name, sname, PRIVILEGE_ADMIN)
  
    def shelf_subscribed(repo_name, _):  # @UnusedVariable
        return _ in e.user.subscriptions
    
    res['shelf_can_read'] = can_read
    res['shelf_can_write'] = can_write           
    res['shelf_can_subscribe'] = can_subscribe
    res['shelf_can_admin'] = can_admin
    res['shelf_subscribed'] = shelf_subscribed           
    
    def library_url(_):
        if _ is None:
            msg = 'library_name = None'
            raise ValueError(msg)
        if e.shelf_name is None:
            msg = 'shelf_name is not set'
            raise ValueError(msg)
        return e.root + '/repos/' + e.repo_name + '/shelves/' + e.shelf_name + '/libraries/' + _
    
    def thing_url(t):
        url = '/repos/{repo_name}/shelves/{shelf_name}/libraries/{library_name}/{spec_name}/%s' % t
        url = e.root + url.format(**e.__dict__)
        return url
    
    res['thing_url'] = thing_url
        
    res['library_url'] = library_url
    def shelf_url(repo_name, shelf_name):
        return e.root  + '/repos/' + repo_name + '/shelves/' + shelf_name
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

    def icon_spec(spec_name):
        return res['icon_%s' % spec_name]
    res['icon_spec'] = icon_spec
    
    def get_user(username):
        user = session.get_user(username)
        return user.dict_for_page()
    
    res['get_user'] = get_user
    
def add_std_vars_context(f):
    return add_std_vars_context_(f,redir=True)

def add_std_vars_context_no_redir(f):
    return add_std_vars_context_(f,redir=False)
    
def add_std_vars_context_(f, redir):
    from .resource_tree import context_display_in_detail, Resource

    def f0(self, context, request):
        if '//' in urlparse.urlparse(request.url).path:
            msg = 'This is an invalid URL with 2 slashes: %s' % request.url
            response =  Response(msg)
            response.status_int = 500
            return response
        if redir:
            url = request.url
            if not url.endswith('/'):
                url2 = url + '/'
                raise HTTPFound(url2)
        
        try:
            res = f(self, context, request)
        except HTTPException:
            raise
        except Exception as e:
            msg = 'While running %s:' % (f.__name__)
            msg += '\n' + indent(traceback.format_exc(e), ' >')
            logger.error(msg)
            raise
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