from mocdp.comp.context import Context, ValueWithUnits
from mocdp.lang.eval_constant_imp import eval_constant
from mocdp.lang.namedtuple_tricks import remove_where_info
from mocdp.lang.parse_actions import parse_wrap
from mocdp.lang.syntax import Syntax
import cgi


class AppInteractive():
    """
        /interactive/mcdp_value/
        /interactive/mcdp_value/parse
        /interactive/mcdp_type/
        
        /interactive/mcdp_model  
    
    """

    def __init__(self):
        pass

    def config(self, config):
        base = '/interactive/'

        config.add_route('mcdp_value', base + 'mcdp_value/')
        config.add_view(self.view_mcdp_value, route_name='mcdp_value', 
                        renderer='interactive_mcdp_value.jinja2')
        config.add_route('mcdp_value_parse', base + 'mcdp_value/parse')
        config.add_view(self.view_mcdp_value_parse, route_name='mcdp_value_parse',
                        renderer='json')

    def view_mcdp_value(self, request):  # @UnusedVariable
        return {}

    def view_mcdp_value_parse(self, request):
        from mcdp_web.app_solver import ajax_error_catch

        string = request.json_body['string']
        assert isinstance(string, unicode)
        string = string.encode('utf-8')

        def go():
            return self.parse(string)
        return ajax_error_catch(go)

    def parse(self, string):
        expr = Syntax.rvalue
        x = parse_wrap(expr, string)[0]
        x = remove_where_info(x)
        context = Context()

        result = eval_constant(x, context)

        assert isinstance(result, ValueWithUnits)
        value = result.value
        space = result.unit
        space.belongs(value)

        res = {}

        e = cgi.escape
        res['output_parsed'] = e(str(x).replace(', where=None', ''))
        res['output_space'] = e(space.__repr__() + '\n' + str(type(space)))
        res['output_raw'] = e(value.__repr__() + '\n' + str(type(value)))
        res['output_formatted'] = e(space.format(value))
        res['ok'] = True

        return res
