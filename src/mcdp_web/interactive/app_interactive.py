# -*- coding: utf-8 -*-
import cgi

from mcdp_web.environment import cr2e
from mcdp_web.resource_tree import ResourceLibraryInteractiveValue, ResourceLibraryInteractiveValueParse
from mcdp_web.utils.ajax_errors import ajax_error_catch
from mcdp_web.utils0 import add_std_vars_context


class AppInteractive(object):
    """
        /libraries/{library}/interactive/mcdp_value/
        /libraries/{library}/interactive/mcdp_value/parse
        
        /interactive/mcdp_type/
        
    """

    def __init__(self):
        pass

    def config(self, config):
        config.add_view(self.view_mcdp_value, context=ResourceLibraryInteractiveValue, 
                        renderer='interactive/interactive_mcdp_value.jinja2')
        config.add_view(self.view_mcdp_value_parse, 
                        context=ResourceLibraryInteractiveValueParse,
                        renderer='json')

    @add_std_vars_context
    def view_mcdp_value(self, context, request):  # @UnusedVariable
        return {}
    @cr2e
    def view_mcdp_value_parse(self, e):
        

        string = e.request.json_body['string']
        assert isinstance(string, unicode)
        string = string.encode('utf-8')

        def go():
            return self.parse(e, string)
        return ajax_error_catch(go, environment=e)

    def parse(self, e, string): 
        result = e.library.parse_constant(string)

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
