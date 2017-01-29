# -*- coding: utf-8 -*-
from mcdp_web.utils.image_error_catch_imp import response_image
from mocdp.memoize_simple_imp import memoize_simple
from system_cmd.meat import system_cmd_result
import os
from compmake.utils.duration_hum import duration_compact


class AppStatus():
    """
       /status/uptime.png
       /status/branch-name.png -  git rev-parse --abbrev-ref HEAD
       /status/branch-date.png - git show --format="%ci" master | head -n 1

    """

    def __init__(self):
        pass

    def config(self, config):
        base = '/status'
        
        route = 'uptime'
        config.add_route(route, base + '/uptime.png')
        config.add_view(self.view_uptime, route_name=route)

        route = 'branch'
        config.add_route(route, base + '/branch-name.png')
        config.add_view(self.view_branch_name, route_name=route)

        route = 'branch-date'
        config.add_route(route, base + '/branch-date.png')
        config.add_view(self.view_branch_date, route_name=route)

    def format_string(self, request, s):
        fontsize = 20
        ratio = 2.5/4
        h = int(fontsize)
        w = int(fontsize * len(s) * ratio)
        size = (w, h)
        green = (0,255,0)
        color = green
        return response_image(request, s, size, color, fontsize)
        
    def view_uptime(self, request):  # @UnusedVariable
        s = duration_compact(self.get_uptime_s())
        return self.format_string(request, s)
        
    def view_branch_name(self, request):  # @UnusedVariable
        s = get_branch_name()
        return self.format_string(request, s)
    
    def view_branch_date(self, request):  # @UnusedVariable
        s = get_branch_date()
        return self.format_string(request, s)

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
    return s.split('\n')[0]
