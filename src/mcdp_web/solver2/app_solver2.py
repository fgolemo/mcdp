from mcdp_cli.solve_meat import solve_meat_solve
from mcdp_posets.types_universe import (express_value_in_isomorphic_space,
    get_types_universe)
from mcdp_web.utils import ajax_error_catch, memoize_simple
from mcdp_dp.tracer import Tracer
import cgi


class AppSolver2():
    """
        /libraries/{library}/models/{models}/views/solver2/
        /libraries/{library}/models/{models}/views/solver2/submit
        
    """

    def __init__(self):
        pass

    def config(self, config):
        self.add_model_view('solver2', desc='Another solver interface')

        base = '/libraries/{library}/models/{model_name}/views/solver2/'
        config.add_route('solver2_base', base)
        config.add_view(self.view_solver2_base, route_name='solver2_base',
                        renderer='solver2/solver2_base.jinja2')

        config.add_route('solver2_submit', base + 'submit')
        config.add_view(self.view_solver2_submit, route_name='solver2_submit',
                        renderer='json')

    @memoize_simple
    def _get_ndp_dp(self, library_name, model_name):
        library = self.libraries[library_name]['library']
        ndp = library.load_ndp(model_name)
        dp = ndp.get_dp()
        return ndp, dp

    def view_solver2_base(self, request):
        model_name = self.get_model_name(request)
        library = self.get_current_library_name(request)
        _ndp, dp = self._get_ndp_dp(library, model_name)

        F = dp.get_fun_space()

        space_description = str(F).decode('utf-8')
        return {'navigation': self.get_navigation_links(request),
                'space_description': space_description}

    def view_solver2_submit(self, request):
        string = request.json_body['string']
        assert isinstance(string, unicode)
        string = string.encode('utf-8')

        def go():
            return self.process(request, string)
        return ajax_error_catch(go)


    def process(self, request, string):
        l = self.get_library(request)
        result = l.parse_constant(string)

        space = result.unit
        value = result.value

        model_name = self.get_model_name(request)
        library = self.get_current_library_name(request)
        ndp, dp = self._get_ndp_dp(library, model_name)

        F = dp.get_fun_space()

        tu = get_types_universe()
        tu.check_leq(result.unit, F)

        f = express_value_in_isomorphic_space(result.unit, result.value, F)

        print('query: %s ...' % F.format(f))
        from mocdp import logger
        tracer = Tracer(logger=logger)

        intervals = False
        max_steps = 10000
        result, trace = solve_meat_solve(tracer, ndp, dp, f,
                                      intervals, max_steps, False)
        print result



        res = {}

        e = cgi.escape
        # res['output_parsed'] = e(str(x).replace(', where=None', ''))
        res['output_space'] = e(space.__repr__() + '\n' + str(type(space)))
        res['output_raw'] = e(value.__repr__() + '\n' + str(type(value)))
        res['output_formatted'] = e(space.format(value))

        res['output_result'] = str(result)
        res['output_trace'] = str(trace)
        res['ok'] = True

        return res

