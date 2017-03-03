import traceback

from compmake.utils.duration_hum import duration_compact
from contracts.utils import check_isinstance, indent
from mcdp import logger
import mcdp
from mcdp_web.get_navigation_links_imp import get_navigation_links_context
from mcdp_library.library import MCDPLibrary
from mcdp_shelf.access import PRIVILEGE_SUBSCRIBE

from pyramid.httpexceptions import HTTPException

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
    
    if request.authenticated_userid is not None:
        username = request.authenticated_userid
        print('authenticated_userid',username)
        user_db = self.user_db
        if username in user_db:
            res['user'] = user_db[username].dict_for_page()
            groups = user_db[username].get_groups()
        else:
            res['user'] = None
            groups = []
    else:
        username = None
        res['user'] = None
        groups = []
    
                
    res['can_subscribe'] = lambda sname: session.shelves_available[sname].get_acl().allowed(PRIVILEGE_SUBSCRIBE, username, groups)
    
    
    
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
        add_other_fields(self, res, request, context=context)
        return res
    return f0