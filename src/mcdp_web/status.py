# -*- coding: utf-8 -*-
import json
import os
import socket
import time

from dateutil.parser import parse
import pyramid

from compmake.utils import duration_compact
import mcdp
from mcdp.utils.memoize_simple_imp import memoize_simple
from system_cmd import system_cmd_result


class AppStatus():
    """
       /status/status.json
    """

    def __init__(self):
        pass

    def config(self, config):
        route = 'status_json'
        config.add_route(route,'/status/status.json')
        config.add_view(self.view_status, route_name=route, renderer='jsonp',
                        permission=pyramid.security.NO_PERMISSION_REQUIRED)


    def view_status(self, request):  # @UnusedVariable
        uptime_s = self.get_uptime_s()
        
        t = get_branch_date()
        dt = time.time() - t
        
        access = 'public' if self.options.allow_anonymous else 'private'
        res = {
            'version': mcdp.__version__,
            'server-name': socket.gethostname(),
            'access': access,
            'geoip': geoip(),
            'branch-date':  t,
            'branch-date-h': duration_compact(dt),
            'branch-name-actual': get_branch_name(),
            'uptime': duration_compact(uptime_s),
            'uptime_s': uptime_s,
            'options': self.options._values, 
            'branch-name': mcdp.BranchInfo.branch_name,
            'branch-topic': mcdp.BranchInfo.branch_topic,
        }
        return res
    
@memoize_simple
def geoip(): 
    url = 'http://freegeoip.net/json/'
    from urllib import urlopen
    s = urlopen(url).read()
    return json.loads(s)
    
    
def get_command_output(cmd):
    cwd = os.getcwd()
    res = system_cmd_result(
           cwd, cmd,
           display_stdout=False,
           display_stderr=False,
           raise_on_error=True)
    return res.stdout

@memoize_simple
def get_branch_name():
    cmd=['git', 'rev-parse', '--abbrev-ref', 'HEAD']
    s = get_command_output(cmd)
    return s

@memoize_simple    
def get_branch_date():
    branch_name = get_branch_name()
    cmd=['git', 'show', '--format=%ci', branch_name]
    s = get_command_output(cmd)
    line = s.split('\n')[0]
    t = parse(line)
    stamp = time.mktime(t.timetuple())
    return stamp


#         
#         route = 'uptime'
#         config.add_route(route, base + '/uptime.png')
#         config.add_view(self.view_uptime, route_name=route)
# 
#         route = 'branch'
#         config.add_route(route, base + '/branch-name.png')
#         config.add_view(self.view_branch_name, route_name=route)
# 
#         route = 'branch-date'
#         config.add_route(route, base + '/branch-date.png')
#         config.add_view(self.view_branch_date, route_name=route)
# 
#     def format_string(self, request, s):
#         fontsize = 20
#         ratio = 2.5/4
#         h = int(fontsize)
#         w = int(fontsize * len(s) * ratio)
#         size = (w, h)
#         green = (0,255,0)
#         black = (0,0,0)
#         color = black
#         return response_image(request, s, size, color, fontsize)
#         
#     def view_uptime(self, request):  # @UnusedVariable
#         s = duration_compact(self.get_uptime_s())
#         return self.format_string(request, s)
#         
#     def view_branch_name(self, request):  # @UnusedVariable
#         s = get_branch_name()
#         return self.format_string(request, s)
#     
#     def view_branch_date(self, request):  # @UnusedVariable
#         s = get_branch_date()
#         return self.format_string(request, s)