from contracts.utils import raise_desc, raise_wrapped
from mcdp_cli.solve_meat import solve_meat_solve
from mcdp_dp.dp_transformations import get_dp_bounds
from mcdp_dp.tracer import Tracer
from mcdp_lang.parse_interface import parse_constant
from mcdp_posets import UpperSets
from mcdp_posets.types_universe import (express_value_in_isomorphic_space,
    get_types_universe)
from mcdp_report.generic_report_utils import get_best_plotter
from mcdp_report.gg_ndp import format_unit
from mcdp_web.utils import ajax_error_catch, memoize_simple, response_data
from mocdp.exceptions import DPSyntaxError, mcdp_dev_warning
from reprep import Report
from reprep.plot_utils.axes import x_axis_extra_space, y_axis_extra_space
import cgi


class AppSolver2():
    """
        /libraries/{library}/models/{models}/views/solver2/
        /libraries/{library}/models/{models}/views/solver2/submit
        
        /libraries/{library}/models/{models}/views/solver2/compact_graph.png
        
        /libraries/{library}/models/{models}/views/solver2/display1u
        /libraries/{library}/models/{models}/views/solver2/display1u.png?
        
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

        config.add_route('view_solver2_display1u_ui', base + 'display1u')
        config.add_view(self.view_solver2_display1u_ui,
                        route_name='view_solver2_display1u_ui',
                        renderer='solver2/solver2_display1u_ui.jinja2')

        config.add_route('view_solver2_display1d', base + 'display1u.png')
        config.add_view(self.view_solver2_display1u, route_name='view_solver2_display1d')

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
        parsed = l.parse_constant(string)

        space = parsed.unit
        value = parsed.value

        model_name = self.get_model_name(request)
        library = self.get_current_library_name(request)
        ndp, dp = self._get_ndp_dp(library, model_name)

        F = dp.get_fun_space()
        UR = UpperSets(dp.get_res_space())

        tu = get_types_universe()
        tu.check_leq(parsed.unit, F)

        f = express_value_in_isomorphic_space(parsed.unit, parsed.value, F)

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


        key = (string, nl, nu)

        res = dict(result_l=result_l, result_u=result_u, dpl=dpl, dpu=dpu)
        self.solutions[key] = res

        res = {}

        e = cgi.escape

        res['output_space'] = e(space.__repr__() + '\n' + str(type(space)))
        res['output_raw'] = e(value.__repr__() + '\n' + str(type(value)))
        res['output_formatted'] = e(space.format(value))

        res['output_result'] = 'Lower: %s\nUpper: %s' % (UR.format(result_l),
                                                         UR.format(result_u))
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
                plotter.plot(pylab, axis, UR, result_l,
                             params=dict(markers='g.', color_shadow='green'))
                plotter.plot(pylab, axis, UR, result_u,
                             params=dict(markers='b.', color_shadow='blue'))


            png_node = r.resolve_url('png')
            png_data = png_node.get_raw_data()

            return response_data(request=request, data=png_data,
                                 content_type='image/png')
        return self.png_error_catch2(request, go)


    def view_solver2_display1u_ui(self, request):
        res = {}
        res['navigation'] = self.get_navigation_links(request)
        return res

    def view_solver2_display1u(self, request):
        """
            Parameters that we need:
            
                xaxis = one of the functions
                yaxis = one of the resources
                
                xmin =
                xmax =
                nsamples = number of samples to interpolate for xmin-xmax
                
                <fname> = constant
        """
        def go():
            xaxis = str(request.params['xaxis'])
            yaxis = str(request.params['yaxis'])

            model_name = self.get_model_name(request)
            library = self.get_current_library_name(request)
            ndp, dp = self._get_ndp_dp(library, model_name)

            fnames = ndp.get_fnames()
            rnames = ndp.get_rnames()

            if not xaxis in fnames:
                msg = 'Could not find function %r.' % xaxis
                raise_desc(ValueError, msg, fnames=fnames)

            if not yaxis in rnames:
                msg = 'Could not find resource %r.' % yaxis
                raise_desc(ValueError, msg, rnames=rnames)

            fsamples = get_samples(request, ndp)

            nl = int(request.params.get('nl', 1))
            nu = int(request.params.get('nu', 1))
            
            dpl, dpu = get_dp_bounds(dp, nl, nu)
            
            def extract_ri(r):
                if len(rnames) == 1:
                    return r
                else:
                    i = rnames.index(yaxis)
                    return r[i]
                
            ru_samples = []
            rl_samples = []
            for f in fsamples:
                rl = dpl.solve(f)
                ru = dpu.solve(f)
                
                mcdp_dev_warning('should use join instead of min')
        
                values = filter(extract_ri, rl.minimals)
                rli = min(values) if values else None
                values = filter(extract_ri, ru.minimals)
                rui = max(values) if values else None

                ru_samples.append(rui)
                rl_samples.append(rli)

            r = Report()
            f = r.figure()
            with f.plot("plot") as pylab:
                pylab.plot(fsamples, rl_samples, 'b.-')
                pylab.plot(fsamples, ru_samples, 'm.-')

                xlabel = xaxis + ' ' + format_unit(ndp.get_ftype(xaxis))
                pylab.xlabel(xlabel)
                ylabel = yaxis + ' ' + format_unit(ndp.get_rtype(yaxis))
                pylab.ylabel(ylabel)
                y_axis_extra_space(pylab)
                x_axis_extra_space(pylab)
                ax = pylab.gca()
                XCOLOR = 'green'
                YCOLOR = 'red'
                ax.tick_params(axis='x', colors=XCOLOR)
                ax.tick_params(axis='y', colors=YCOLOR)
                ax.yaxis.label.set_color(YCOLOR)
                ax.xaxis.label.set_color(XCOLOR)

                ax.spines['bottom'].set_color(XCOLOR)
                ax.spines['left'].set_color(YCOLOR)

            png_node = r.resolve_url('png')
            png_data = png_node.get_raw_data()

            return response_data(request=request, data=png_data,
                                 content_type='image/png')

        return self.png_error_catch2(request, go)

def get_samples(request, ndp):
    xaxis = str(request.params['xaxis'])
    # yaxis = str(request.params['yaxis'])
    xmin = request.params['xmin'].encode('utf-8')
    xmax = request.params['xmax'].encode('utf-8')
    nsamples = int(request.params['nsamples'])

    fnames = ndp.get_fnames()
    rnames = ndp.get_rnames()


    # must pass the other functions as parameters
    f = {}
    for fn in fnames:
        if fn == xaxis: continue
        if not fn in request.params:
            msg = 'You have to pass the value of function %r.' % fn
            raise_desc(ValueError, msg, rnames=rnames)

        s = request.params[fn]
        try:
            val = parse_constant(s)
        except DPSyntaxError as e:
            msg = 'Cannot parse value for %r.' % fn
            raise_wrapped(ValueError, e, msg, compact=True)

        F = ndp.get_ftype(fn)
        f[fn] = express_value_in_isomorphic_space(val.unit, val.value, F)

    F = ndp.get_ftype(xaxis)
    try:
        xmin = parse_constant(xmin)
        xmax = parse_constant(xmax)
    except DPSyntaxError as e:
        msg = 'Cannot parse value for xmax/xmin.'
        raise_wrapped(ValueError, e, msg, compact=True)

    xmin = express_value_in_isomorphic_space(xmin.unit, xmin.value, F)
    xmax = express_value_in_isomorphic_space(xmax.unit, xmax.value, F)


    import numpy as np
    xsamples = np.linspace(xmin, xmax, nsamples)
    samples = []
    for xsample in xsamples:
        t = []
        for fn in fnames:
            if fn == xaxis:
                t.append(xsample)
            else:
                t.append(f[fn])
        sample = tuple(t)
        if len(fnames) == 1:
            sample = sample[0]

        samples.append(sample)

    return samples

