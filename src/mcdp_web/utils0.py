# -*- coding: utf-8 -*-
import traceback

from contracts.utils import check_isinstance, indent
from pyramid.httpexceptions import HTTPException, HTTPFound

from mcdp import MCDPConstants
from mcdp import logger
import mcdp
from mcdp_shelf import PRIVILEGE_SUBSCRIBE, PRIVILEGE_READ,\
    PRIVILEGE_WRITE, PRIVILEGE_ADMIN
from mcdp_utils_misc import duration_compact

from .environment import Environment
from .get_navigation_links_imp import get_navigation_links_context
from .resource_tree import context_display_in_detail, Resource


def add_other_fields(self, res, request, context):
    e = Environment(context, request)
    res['navigation'] = get_navigation_links_context(e)   
    res['navigation'].update(e.__dict__)         
    res['version'] = lambda: mcdp.__version__  # @UndefinedVariable
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
    
    def shelf_privilege(sname, privilege):
        acl = session.shelves_available[sname].get_acl()
        return acl.allowed2(privilege, user)
         
    def can_subscribe(sname):
        return shelf_privilege(sname, PRIVILEGE_SUBSCRIBE)
    def can_read(sname):
        return shelf_privilege(sname, PRIVILEGE_READ)
    def can_write(sname):
        return shelf_privilege(sname, PRIVILEGE_WRITE)
    def can_admin(sname):
        return shelf_privilege(sname, PRIVILEGE_ADMIN)
  
    def shelf_subscribed(_):
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
    res['shelf_url'] = lambda _: e.root  + '/repos/' + e.repo_name + '/shelves/' + _ 
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
    def f0(self, context, request):
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