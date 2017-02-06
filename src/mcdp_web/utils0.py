from contracts.utils import check_isinstance, indent
import mocdp
from mocdp import logger
import traceback
from compmake.utils.duration_hum import duration_compact

def add_other_fields(self, res, request):
    res['navigation'] = self.get_navigation_links(request)
    
    res['version'] = lambda: mocdp.__version__
    res['root'] =  self.get_root_relative_to_here(request)

    # template functions
    res['render_library_doc'] = lambda docname: self._render_library_doc(request, docname)
    res['has_library_doc'] = lambda docname: self._has_library_doc(request, docname)
    res['uptime_s'] = int(self.get_uptime_s())
    res['uptime_string'] = duration_compact(res['uptime_s'])
    res['time_start'] = self.time_start
    res['authenticated_userid'] = request.authenticated_userid
    
    if request.authenticated_userid is not None:
        u0 = request.authenticated_userid
        from mcdp_web.security import USERS
        if not u0 in USERS:
            res['user'] = None
        else:
            u = USERS[u0]._asdict()
            del u['password']
            res['user'] = u
    else:
        res['user'] = None
    
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
