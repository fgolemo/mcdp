# -*- coding: utf-8 -*-
import traceback

from contracts.utils import check_isinstance, indent
from pyramid.httpexceptions import HTTPException

from compmake.utils.duration_hum import duration_compact
from mcdp import logger
import mcdp
from mcdp_library.library import MCDPLibrary
from mcdp_shelf.access import PRIVILEGE_SUBSCRIBE, PRIVILEGE_READ,\
    PRIVILEGE_WRITE, PRIVILEGE_ADMIN
from mcdp_web.get_navigation_links_imp import get_navigation_links_context
from mcdp_web.resource_tree import context_display_in_detail, Resource


def add_other_fields(self, res, request, context=None):
    if context is None:
        res['navigation'] = self.get_navigation_links(request)
    else:
        res['navigation'] = get_navigation_links_context(self, context, request)
            
    res['version'] = lambda: mcdp.__version__  # @UndefinedVariable
    res['root'] = self.get_root_relative_to_here(request)
    
    if context is None:
        library = self.get_library(request)
    else:
        library = self.get_library(request, context)
        
    def _has_library_doc(document):
        filename = '%s.%s' % (document, MCDPLibrary.ext_doc_md)
        return library.file_exists(filename)
    
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
    
    res['shelf_can_read'] = can_read
    res['shelf_can_write'] = can_write           
    res['shelf_can_subscribe'] = can_subscribe
    res['shelf_can_admin'] = can_admin           
    
    
    
def add_std_vars(f):
    def f0(self, request):
        try:
            res = f(self, request)
        except Exception as e:
            msg = 'While running %s:' % (f.__name__)
            msg += '\n' + indent(traceback.format_exc(e), ' >')
            logger.error(msg)
            raise
        check_isinstance(res, dict)
        add_other_fields(self, res, request)
        return res
    return f0


def add_std_vars_context(f):
    def f0(self, context, request):
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