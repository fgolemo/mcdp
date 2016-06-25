from mcdp_cli.solve_meat import solve_meat_solve
from mcdp_dp.tracer import Tracer
from mcdp_posets.types_universe import (express_value_in_isomorphic_space,
    get_types_universe)
from mcdp_web.utils import ajax_error_catch, memoize_simple
import cgi
from mcdp_dp.dp_transformations import get_dp_bounds
from mcdp_posets.uppersets import UpperSets
from reprep import Report
from mcdp_report.generic_report_utils import generic_plot, get_best_plotter
from mcdp_web.utils.response import response_data
from mcdp_web.utils.image_error_catch_imp import png_error_catch


class AppSolver2():
    """
        /libraries/{library}/models/{models}/views/solver2/
        /libraries/{library}/models/{models}/views/solver2/submit
        
    """

    def __init__(self):
        self.solutions = {}

    def config(self, config):
        self.add_model_view('solver2', desc='Another solver interface')

        base = '/libraries/{library}/models/{model_name}/views/solver2/'

        config.add_route('solver2_base', base)
        config.add_view(self.view_solver2_base, route_name='solver2_base',
                        renderer='solver2/solver2_base.jinja2')

        config.add_route('solver2_submit', base + 'submit')
        config.add_view(self.view_solver2_submit, route_name='solver2_submit',
                        renderer='json')

        config.add_route('solver2_display', base + 'display.png')
        config.add_view(self.view_solver2_display, route_name='solver2_display')

        config.add_route('solver2_image', base + 'compact_graph.png')
        config.add_view(self.image, route_name='solver2_image')

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
        def go():
            string = request.json_body['string']
            assert isinstance(string, unicode)
            string = string.encode('utf-8')

            nl = int(request.json_body['nl'])
            nu = int(request.json_body['nu'])
            return self.process(request, string, nl, nu)

        return ajax_error_catch(go)


    def process(self, request, string, nl, nu):
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

        dpl, dpu = get_dp_bounds(dp, nl, nu)

        intervals = False
        max_steps = 10000
        result_l, trace = solve_meat_solve(tracer, ndp, dpl, f,
                                         intervals, max_steps, False)

        result_u, trace = solve_meat_solve(tracer, ndp, dpu, f,
                                         intervals, max_steps, False)
        print result_l, result_u


        key = (string, nl, nu)
        print key
        res = dict(result_l=result_l, result_u=result_u, dpl=dpl, dpu=dpu)
        self.solutions[key] = res

        res = {}

        e = cgi.escape

        res['output_space'] = e(space.__repr__() + '\n' + str(type(space)))
        res['output_raw'] = e(value.__repr__() + '\n' + str(type(value)))
        res['output_formatted'] = e(space.format(value))

        res['output_result'] = str(result)
        res['output_trace'] = str(trace)

        encoded = "nl=%s&nu=%s&string=%s" % (nl, nu, string)
        res['output_image'] = 'display.png?' + encoded
        res['ok'] = True

        return res

    def view_solver2_display(self, request):
        def go():
            key = (str(request.params['string']),
                   int(request.params['nl']),
                   int(request.params['nu']))
            s = self.solutions[key]

            result_l = s['result_l']
            result_u = s['result_u']
            # print result_l, result_u
            dpl = s['dpl']
            dpu = s['dpu']

            R = dpl.get_res_space()
            UR = UpperSets(R)
            r = Report()
            f = r.figure()
            plotter = get_best_plotter(space=UR)
            # print plotter
            # generic_plot(f, space=UR, value=result_l)

            axis = plotter.axis_for_sequence(UR, [result_l, result_u])

            with f.plot("plot") as pylab:
                plotter.plot(pylab, axis, UR, result_l, params=dict(markers='g.'))
                plotter.plot(pylab, axis, UR, result_u, params=dict(markers='b.',
                                                                    color_shadow='green'))


            png_node = r.resolve_url('png')
            png_data = png_node.get_raw_data()

            return response_data(request=request, data=png_data,
                                 content_type='image/png')
        return png_error_catch(go, request)
