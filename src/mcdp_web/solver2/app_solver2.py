# -*- coding: utf-8 -*-
import base64
import cgi
from contextlib import contextmanager
import json
from mcdp import logger
from mcdp.exceptions import DPSyntaxError, mcdp_dev_warning, DPSemanticError, \
    DPInternalError
from mcdp_cli.solve_meat import solve_meat_solve_rtof, solve_meat_solve_ftor
from mcdp_dp.dp_transformations import get_dp_bounds
from mcdp_dp.primitive import NotSolvableNeedsApprox
from mcdp_dp.tracer import Tracer
from mcdp_lang.parse_interface import parse_constant
from mcdp_posets import express_value_in_isomorphic_space, LowerSets,  NotLeq, UpperSets
from mcdp_report.gg_ndp import format_unit
from mcdp_report.plotters.get_plotters_imp import get_best_plotter
from mcdp_web.environment import cr2e
from mcdp_web.resource_tree import ResourceThingViewSolver,\
    ResourceThingViewSolver_submit,\
    ResourceThingViewSolver_display_png, ResourceThingViewSolver_display1u,\
    ResourceThingViewSolver_display1u_png
from mcdp_web.utils import ajax_error_catch, memoize_simple, response_data
from mcdp_web.utils.image_error_catch_imp import response_image
from mcdp_web.utils0 import add_std_vars_context

from contracts.utils import raise_desc, raise_wrapped
from reprep import Report
from reprep.constants import MIME_PNG
from reprep.plot_utils.axes import x_axis_extra_space, y_axis_extra_space

import numpy as np
from mcdp_web.context_from_env import library_from_env


# Alternate chars used for Base64 instead of + / which give problems with urls
altchars = '-_' 
QUERY_TYPE_FTOR = 'ftor'
QUERY_TYPE_RTOF = 'rtof'

class NeedsApprox(Exception):
    pass

class AppSolver2(object):
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
        config.add_view(self.view_solver2_base, 
                        context=ResourceThingViewSolver, 
                        renderer='solver2/solver2_base.jinja2')

        config.add_view(self.view_solver2_submit, 
                        context=ResourceThingViewSolver_submit,
                        renderer='json')
        
        config.add_view(self.view_solver2_display,
                        context=ResourceThingViewSolver_display_png)
        
        config.add_view(self.view_solver2_display1u_ui,
                        context=ResourceThingViewSolver_display1u,
                        renderer='solver2/solver2_display1u_ui.jinja2')
        
        config.add_view(self.view_solver2_display1u, 
                        context=ResourceThingViewSolver_display1u_png)

    def get_ndp_dp_e(self, e):
        return self.get_ndp_dp(e=e,
                              repo_name=e.repo_name, 
                              shelf_name=e.shelf_name, 
                              library_name=e.library_name, 
                              model_name=e.thing_name)

    def get_ndp_dp(self, e, repo_name, shelf_name, library_name, model_name):
# #         self._xxx_session = session
#         return self._get_ndp_dp(repo_name, shelf_name, library_name, model_name)
#     
#     @memoize_simple
#     def _get_ndp_dp(self, repo_name, shelf_name, library_name, model_name):
#         library = self._xxx_session.libraries[library_name]['library']
#         
        mcdp_library = library_from_env(e)
        
        ndp = e.spec.load(mcdp_library, e.thing_name)
        
#         ndp = library.load_ndp(model_name)
        dp = ndp.get_dp()
        return ndp, dp

    @add_std_vars_context
    @cr2e
    def view_solver2_base(self, e):
        # you don't want to memoize
        ndp, dp = self.get_ndp_dp_e(e)

        F = dp.get_fun_space()
        R = dp.get_res_space()
        I = dp.get_imp_space()

        F_description = str(F)
        R_description = str(R)
        I_description = str(I)
        
        u = lambda s: unicode(s, 'utf-8')
        res =  { 
            'F_description': u(F_description),
            'R_description': u(R_description),
            'F_names': ", ".join(ndp.get_fnames()),
            'R_names': ", ".join(ndp.get_rnames()),
            'I_description': u(I_description),
        } 
        return res

    @cr2e
    def view_solver2_submit(self, e):
        def go():
            state = e.request.json_body['ui_state']
            area_F = state['area_F'].encode('utf-8')
            area_R = state['area_R'].encode('utf-8')
            is_ftor = state['ftor_checkbox']
            is_rtof = state['rtof_checkbox']
            if is_ftor: 
                pass
            elif is_rtof:
                pass
            else:
                msg = 'Cannot establish query type. '
                raise_desc(DPInternalError, msg, state=state)
                
            do_approximations = state['do_approximations']
            nl = state['nl'] 
            nu = state['nu'] 
            
            if is_ftor:
                key = dict(type=QUERY_TYPE_FTOR, 
                            string=area_F, 
                            do_approximations=do_approximations,
                            nu=nu, nl=nl)
        
                data, res = self.process_ftor(e, area_F, do_approximations, nl, nu)
            elif is_rtof:
                key = dict(type=QUERY_TYPE_RTOF, 
                            string=area_R, 
                            do_approximations=do_approximations,
                            nu=nu, nl=nl)

                data, res = self.process_rtof(e, area_R, do_approximations, nl, nu)
            else:
                raise_desc(DPInternalError, 'Inconsistent state', state=state)
        
            key_stable = sorted(tuple(key.items()))  
            h = base64.b64encode(json.dumps(key_stable), altchars=altchars)
    
            data['state'] = state
            data['key'] = key

            self.solutions[h] = data

            res['output_image'] = 'display.png?hash=%s' % h
            res['ok'] = True
            return res
   
        quiet = (DPSyntaxError, DPSemanticError, NeedsApprox)
        return ajax_error_catch(go, quiet=quiet, environment=e)
    
    def process_rtof(self, e, string, do_approximations, nl, nu):
        mcdp_library = library_from_env(e)
        parsed = mcdp_library.parse_constant(string)


        space = parsed.unit
        value = parsed.value

        ndp, dp = self.get_ndp_dp_e(e)

        R = dp.get_res_space()
        LF = LowerSets(dp.get_fun_space())

        try:
            r = parsed.cast_value(R)
        except NotLeq: 
            msg = 'Space %s cannot be converted to %s' % (parsed.unit, R)
            raise DPSemanticError(msg)

        logger.info('query rtof: %s ...' % R.format(r))
        tracer = Tracer(logger=logger)
        
        max_steps = 10000
        intervals = False  
        
        res = {}
        if do_approximations:
    
            dpl, dpu = get_dp_bounds(dp, nl, nu)
    
            result_l, _trace = solve_meat_solve_rtof(tracer, ndp, dpl, r,
                                                intervals, max_steps, False)
    
            result_u, trace = solve_meat_solve_rtof(tracer, ndp, dpu, r,
                                               intervals, max_steps, False)
            
            data = dict(result_l=result_l, result_u=result_u, dpl=dpl, dpu=dpu)
            
            res['output_result'] = 'Lower: %s\nUpper: %s' % (LF.format(result_l),
                                                            LF.format(result_u))
        else:
            try:
                result, trace = solve_meat_solve_rtof(tracer, ndp, dp, r,
                                               intervals, max_steps, False)
            except NotSolvableNeedsApprox:
                msg = 'The design problem has infinite antichains. Please use approximations.'
                raise NeedsApprox(msg)    

            data = dict(result=result, dp=dp)
            res['output_result'] = LF.format(result)
                
        e = cgi.escape

        res['output_space'] = e(space.__repr__() + '\n' + str(type(space)))
        res['output_raw'] = e(value.__repr__() + '\n' + str(type(value)))
        res['output_formatted'] = e(space.format(value))
        res['output_trace'] = str(trace) 
         
        return data, res

    def process_ftor(self, e, string, do_approximations, nl, nu):
        mcdp_library = library_from_env(e)
        parsed = mcdp_library.parse_constant(string)

        space = parsed.unit
        value = parsed.value
         
        
        ndp, dp = self.get_ndp_dp_e(e)
        
        F = dp.get_fun_space()
        UR = UpperSets(dp.get_res_space())

        try:
            f = parsed.cast_value(F)
        except NotLeq: 
            msg = 'Space %s cannot be converted to %s' % (parsed.unit, F)
            raise DPSemanticError(msg)

        logger.info('query rtof: %s ...' % F.format(f))
 
        tracer = Tracer(logger=logger)
        
        intervals = False
        max_steps = 10000
        res = {}

        if do_approximations:
    
            dpl, dpu = get_dp_bounds(dp, nl, nu)
         
            result_l, _trace = solve_meat_solve_ftor(tracer, ndp, dpl, f,
                                             intervals, max_steps, False)
    
    
            result_u, trace = solve_meat_solve_ftor(tracer, ndp, dpu, f,
                                             intervals, max_steps, False)
            
            data = dict(result_l=result_l, result_u=result_u, dpl=dpl, dpu=dpu)

            res['output_result'] = 'Lower: %s\nUpper: %s' % (UR.format(result_l),
                                                         UR.format(result_u))

        else:
            try:
                result, trace = solve_meat_solve_ftor(tracer, ndp, dp, f,
                                                   intervals, max_steps, False)
            except NotSolvableNeedsApprox:
                msg = 'The design problem has infinite antichains. Please use approximations.'
                raise NeedsApprox(msg)    
            data = dict(result=result, dp=dp)
            
            res['output_result'] = UR.format(result)

        e = cgi.escape
        res['output_space'] = e(space.__repr__() + '\n' + str(type(space)))
        res['output_raw'] = e(value.__repr__() + '\n' + str(type(value)))
        res['output_formatted'] = e(space.format(value))
        res['output_trace'] = str(trace) 
        return data, res

    @cr2e
    def view_solver2_display(self, e):

        def go():
            h =e. request.params['hash'].encode('utf-8')
            if not h in self.solutions:
                try:
                    h2 = base64.b64decode(h, altchars=altchars)
                    decoded = json.loads(h2)
                except Exception:
                    decoded = '(unparsable)'
                
                msg = 'Cannot find solution from hash.'
                others = list(self.solutions)
                raise_desc(DPInternalError, msg, h=h, decoded=decoded, others=others)
                #logger.error('do not have solution for %s' % orig)
            data = self.solutions[h]
            key = data['key']
            
            if key['type'] == QUERY_TYPE_FTOR:
                
                if key['do_approximations']:
                    result_l, result_u = data['result_l'], data['result_u']
        
                    dpl, _dpu = data['dpl'], data['dpu']

                    R = dpl.get_res_space()
                    UR = UpperSets(R)
                    
                    output = {}
                    with save_plot(output) as pylab:
                        plotter = get_best_plotter(space=UR)
                        axis = plotter.axis_for_sequence(UR, [result_l, result_u])
                        plotter.plot(pylab, axis, UR, result_l,
                                     params=dict(markers='g.', color_shadow='orange'))
                        plotter.plot(pylab, axis, UR, result_u,
                                     params=dict(markers='b.', color_shadow='blue'))
        
                    png = output['png']
                    return response_data(e.request, png, MIME_PNG)
                else:
                    result = data['result'] 
                    dp = data['dp']
                    R = dp.get_res_space()
                    UR = UpperSets(R)
                    
                    output = {}
                    with save_plot(output) as pylab:
                        plotter = get_best_plotter(space=UR)
                        axis = plotter.axis_for_sequence(UR, [result])
                        plotter.plot(pylab, axis, UR, result,
                                     params=dict(markers='r.', color_shadow='darkred'))
        
                    png = output['png']
                    return response_data(e.request, png, MIME_PNG)
            else:
                msg = 'Cannot display this.'
                return response_image(e.request, msg, color=(125,125,125))
        
        return self.png_error_catch2(e.request, go)


    @cr2e
    def view_solver2_display1u_ui(self, e):  # @UnusedVariable
        return {}

    @cr2e
    def view_solver2_display1u(self, e):
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
            xaxis = str(e.request.params['xaxis'])
            yaxis = str(e.request.params['yaxis'])
 
            ndp, dp = self.get_ndp_dp_e(e)

            fnames = ndp.get_fnames()
            rnames = ndp.get_rnames()

            if not xaxis in fnames:
                msg = 'Could not find function %r.' % xaxis
                raise_desc(ValueError, msg, fnames=fnames)

            if not yaxis in rnames:
                msg = 'Could not find resource %r.' % yaxis
                raise_desc(ValueError, msg, rnames=rnames)

            fsamples = get_samples(e.request, ndp)

            nl = int(e.request.params.get('nl', 1))
            nu = int(e.request.params.get('nu', 1))
            
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

            return response_data(request=e.request, data=png_data,
                                 content_type='image/png')

        return self.png_error_catch2(e.request, go)

@contextmanager
def save_plot(output):
    """
        output = {}
        with save_plot(output) as pylab:
            pylab.plot(0,0)
    """
    r = Report()
    f = r.figure()
    with f.plot("plot") as pylab:
        yield pylab
    output['png'] = r.resolve_url('png').get_raw_data()
    output['pdf'] = r.resolve_url('plot').get_raw_data()
    
     

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

