
from contracts import contract
from mocdp.posets.uppersets import UpperSets

class SolverState():
    def __init__(self, ndp):
        self.fun = []
        self.ures = []
        self.ndp = ndp
        dp = self.ndp.get_dp()
        self.dp = dp

    def new_point(self, point):
        self.fun.append(point)
        ures = self.dp.solve(point)
        F = self.dp.get_fun_space()
        R = self.dp.get_res_space()
        UR = UpperSets(R)
        # print('f = %s -> %s' % (F.format(point), UR.format(ures)))
        self.ures.append(ures)

    @contract(fun_index='seq[2](int)',
              res_index='seq[2](int)')
    def get_data_for_js(self, fun_index, res_index):
        ndp = self.ndp
        fn1 = ndp.get_fnames()[fun_index[0]]
        fn2 = ndp.get_fnames()[fun_index[1]]
        rn1 = ndp.get_rnames()[fun_index[0]]
        rn2 = ndp.get_rnames()[fun_index[1]]

        res = {}
        res['datasets_fun'] = self.get_datasets_fun(fun_index)
        res['datasets_res'] = self.get_datasets_res(res_index)

        def fun_label(fn):
            return fn + ' [%s]' % self.ndp.get_ftype(fn)

        def res_label(rn):
            return rn + ' [%s]' % self.ndp.get_rtype(rn)

        res['fun_xlabel'] = fun_label(fn1)
        res['fun_ylabel'] = fun_label(fn2)
        res['res_xlabel'] = res_label(rn1)
        res['res_ylabel'] = res_label(rn2)

        return res

    def get_color(self, i):
        colors = ['green', 'blue', 'brown']
        color = colors[ i % len(colors) ]
        n = len(self.fun)
        if i < n - 3:
            color = 'gray'

        infeasible = len(self.ures[i].minimals) == 0
        if infeasible:
            return 'red'
        return color

    def get_datasets_fun(self, fun_index):
        # one dataset per point in fun
        def make_point(p):
            return {'x': p[fun_index[0]], 'y': p[fun_index[1]]}
#
#         def get_marker(i):
#             if len(self.ures[i].minimals) != 0:
#                 return "cross"
#             else:
#                 return "circle"

        datasets = [{'data': [make_point(p)],
                 'backgroundColor': self.get_color(i)} for i, p in enumerate(self.fun)]
#         print datasets
        return datasets

    def get_datasets_res(self, res_index):
        # one dataset per point in fun

        def make_point(p):
            return {'x': p[res_index[0]], 'y': p[res_index[1]]}

        def get_points(ui):
            return [make_point(p) for p in ui.minimals]

        return [{'data': get_points(ui),
                 'backgroundColor': self.get_color(i)} for i, ui in enumerate(self.ures)]

class AppSolver():
    """
        /solver/batteries/0,1/0,1   presents the gui. 0,1 are the axes
    
        /solver_addpoint/batteries params x, y
        /solver_getdatasets/batteries params -
        /solver_reset/batteries params -
        
    """

    def __init__(self):
        self.solver_states = {}

    def get_solver_state(self, request):
        params = self.parse_params(request)
        model_name = params['model_name']
        if not model_name in self.solver_states:
            self.reset(request)
        return self.solver_states[model_name]

    def reset(self, request):
        params = self.parse_params(request)
        model_name = params['model_name']
        _, self.ndp = self.get_library().load_ndp(model_name)
        self.solver_states[model_name] = SolverState(self.ndp)

    def config(self, config):
        config.add_route('solver', '/solver/{model_name}/{fun_axes}/{res_axes}/')
        config.add_view(self.view_solver, route_name='solver',
                        renderer='interactive.jinja2')

        config.add_route('solver_addpoint', '/solver/{model_name}/{fun_axes}/{res_axes}/addpoint')
        config.add_view(self.view_solver_addpoint,
                        route_name='solver_addpoint', renderer='json')

        config.add_route('solver_getdatasets', '/solver/{model_name}/{fun_axes}/{res_axes}/getdatasets')
        config.add_view(self.view_solver_getdatasets, route_name='solver_getdatasets', renderer='json')

        config.add_route('solver_reset', '/solver/{model_name}/{fun_axes}/{res_axes}/reset')
        config.add_view(self.view_solver_reset,
                        route_name='solver_reset', renderer='json')


    def view_solver_reset(self, request):
        self.reset(request)
        return self.return_new_data(request)
        
    def parse_params(self, request):
        model_name = str(request.matchdict['model_name'])  # unicod
        fun_axes = map(int, request.matchdict['fun_axes'].split(','))
        res_axes = map(int, request.matchdict['res_axes'].split(','))
        return {'model_name': model_name,
                'fun_axes':fun_axes,
                'res_axes': res_axes}

    def view_solver(self, request):
        params = self.parse_params(request)
        solver_state = self.get_solver_state(request)

        ndp = solver_state.ndp
        
        fnames = ndp.get_fnames()
        rnames = ndp.get_rnames()
        fun_names = [fnames[i] for i in params['fun_axes']]
        res_names = [rnames[i] for i in params['res_axes']]
        # these are not included
        fun_names_other = [fn for fn in fnames if not fn in fun_names]
        # check that the axes are compatible

        print fun_names_other
        return {'model_name': params['model_name'],
                'fun_names': fun_names,
                'res_names': res_names,
                'fun_names_other': fun_names_other}

    def return_new_data(self, request):
        solver_state = self.get_solver_state(request)
        params = self.parse_params(request)

        fun_axes = params['fun_axes']
        res_axes = params['res_axes']
#         raise HTTPFound('/solver/%s/%s/%s/getdatasets' % (model_name, fun_axes, res_axes))
#

# #         try:
# #             pass
#         except Exception as e:
#             res = {}
#             res['ok'] = False
#             res['error'] = traceback.format_exc(e)
#             return res
#         else:
        res = {}
        res['ok'] = True
        data = solver_state.get_data_for_js(fun_axes, res_axes)
        res.update(**data)
        return res

    def view_solver_getdatasets(self, request):
        return self.return_new_data(request)

    def view_solver_addpoint(self, request):
        solver_state = self.get_solver_state(request)

        x = float(request.params['x'])
        y = float(request.params['y'])

        solver_state.new_point((x, y))
        return self.return_new_data(request)

