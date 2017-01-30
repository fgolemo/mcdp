# -*- coding: utf-8 -*-
import cgi

from mcdp_web.utils0 import add_std_vars


class AppInteractive():
    """
        /libraries/{library}/interactive/mcdp_value/
        /libraries/{library}/interactive/mcdp_value/parse
        
        /interactive/mcdp_type/
        
    """

    def __init__(self):
        pass

    def config(self, config):
        base = '/libraries/{library}/interactive/'

        config.add_route('mcdp_value', base + 'mcdp_value/')
        config.add_view(self.view_mcdp_value, route_name='mcdp_value', 
                        renderer='interactive/interactive_mcdp_value.jinja2')
        config.add_route('mcdp_value_parse', base + 'mcdp_value/parse')
        config.add_view(self.view_mcdp_value_parse, route_name='mcdp_value_parse',
                        renderer='json')

    @add_std_vars
    def view_mcdp_value(self, request):  # @UnusedVariable
        return {}

    def view_mcdp_value_parse(self, request):
        from mcdp_web.solver.app_solver import ajax_error_catch

        string = request.json_body['string']
        assert isinstance(string, unicode)
        string = string.encode('utf-8')

        def go():
            return self.parse(request, string)
        return ajax_error_catch(go)

    def parse(self, request, string):
        l = self.get_library(request)
        result = l.parse_constant(string)

        space = result.unit
        value = result.value

        res = {}

        e = cgi.escape
        # res['output_parsed'] = e(str(x).replace(', where=None', ''))
        res['output_space'] = e(space.__repr__() + '\n' + str(type(space)))
        res['output_raw'] = e(value.__repr__() + '\n' + str(type(value)))
        res['output_formatted'] = e(space.format(value))
        res['ok'] = True

        return res
