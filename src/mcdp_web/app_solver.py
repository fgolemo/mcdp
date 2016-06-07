import itertools
from mcdp_web.app_solver_state import SolverState, get_decisions_for_axes
import traceback
from mocdp.dp_report.gg_ndp import STYLE_GREENREDSYM, gvgen_from_ndp
from cdpview.plot import png_pdf_from_gg
from mcdp_web.utils import response_data
from pyramid.httpexceptions import HTTPSeeOther
from mocdp.exceptions import DPSemanticError, DPSyntaxError

class AppSolver():
    """
        /solver/batteries/   - redirects to one with the right amount of axis
    
        /solver/batteries/0,1/0,1/   presents the gui. 0,1 are the axes
    
        AJAX:
            /solver/batteries/0,1/0,1/addpoint     params x, y
            /solver/batteries/0,1/0,1/getdatasets  params -
            /solver/batteries/0,1/0,1/reset        params -
            
        /solver/batteries/0,1/0,1/compact_graph    png image
        /solver/batteries/compact_graph    png image
    """

    def __init__(self):
        self.solver_states = {}

    def get_model_name(self, request):
        return str(request.matchdict['model_name'])  # unicode

    def get_solver_state(self, request):
        model_name = self.get_model_name(request)
        if not model_name in self.solver_states:
            self.reset(request)
        return self.solver_states[model_name]

    def reset(self, request):
        model_name = self.get_model_name(request)
        _, self.ndp = self.get_library().load_ndp(model_name)
        self.solver_states[model_name] = SolverState(self.ndp)

    def config(self, config):
        base = '/solver/{model_name}/{fun_axes}/{res_axes}/'

        config.add_route('solver_base', "/solver/{model_name}/")
        config.add_view(self.view_solver_base,
                        route_name='solver_base', renderer='solver.jinja2')

        config.add_route('solver', base)
        config.add_view(self.view_solver,
                        route_name='solver', renderer='solver.jinja2')

        config.add_route('solver_addpoint', base + 'addpoint')
        config.add_view(self.ajax_solver_addpoint,
                        route_name='solver_addpoint', renderer='json')

        config.add_route('solver_getdatasets', base + 'getdatasets')
        config.add_view(self.ajax_solver_getdatasets,
                        route_name='solver_getdatasets', renderer='json')

        config.add_route('solver_reset', base + 'reset')
        config.add_view(self.ajax_solver_reset,
                        route_name='solver_reset', renderer='json')

        config.add_route('solver_image', base + 'compact_graph')
        config.add_view(self.image, route_name='solver_image')
        config.add_route('solver_image2', '/solver/{model_name}/compact_graph')
        config.add_view(self.image, route_name='solver_image2')

    def parse_params(self, request):
        model_name = self.get_model_name(request)

        fun_axes = map(int, request.matchdict['fun_axes'].split(','))
        res_axes = map(int, request.matchdict['res_axes'].split(','))
        return {'model_name': model_name,
                'fun_axes': fun_axes,
                'res_axes': res_axes}

    def view_solver_base(self, request):
        model_name = self.get_model_name(request)

        solver_state = self.get_solver_state(request)
        ndp = solver_state.ndp
        nf = len(ndp.get_fnames())
        nr = len(ndp.get_rnames())

        base = '/solver/%s' % model_name
        if nf >= 2 and nr >= 2:
            url = '/0,1/0,1/'
            raise HTTPSeeOther(base + url)
        elif nf == 1 and nr >= 2:
            url = '/0/0,1/'
            raise HTTPSeeOther(base + url)
        else:
            title = 'Could not find render view for this model. '
            message = 'Could not find render view for this model. '
            message += '<br/>'
            message += str(ndp)
            return {'title': title, 'message': message}

        
    def view_solver(self, request):
        params = self.parse_params(request)
        solver_state = self.get_solver_state(request)

        ndp = solver_state.ndp
        fnames = ndp.get_fnames()
        fun_axes = params['fun_axes']
        res_axes = params['res_axes']

        decisions = get_decisions_for_axes(ndp, fun_axes, res_axes)
        # these are not included
        included = [fnames[_] for _ in fun_axes]
        fun_names_other = [fn for fn in fnames if not fn in included]
        # check that the axes are compatible

        fun_alternatives, res_alternatives = create_alternative_urls(params, ndp)

        res = {'model_name': params['model_name'],
                'fun_name_x': decisions['fun_name_x'],
                'fun_name_y': decisions['fun_name_y'],
                'res_name_x': decisions['res_name_x'],
                'res_name_y': decisions['res_name_y'],
                'fun_names_other': fun_names_other,
                'res_alternatives': res_alternatives,
                'fun_alternatives': fun_alternatives,
                'current_url': request.path,
                'params': params}
        return res

    def return_new_data(self, request):
        solver_state = self.get_solver_state(request)
        params = self.parse_params(request)
        
        fun_axes = params['fun_axes']
        res_axes = params['res_axes']

        res = {}
        res['ok'] = True
        data = solver_state.get_data_for_js(fun_axes, res_axes)
        res.update(**data)
        return res

    def ajax_solver_getdatasets(self, request):
        def go():
            return self.return_new_data(request)
        return ajax_error_catch(go)

    def ajax_solver_addpoint(self, request):        
        def go():
            solver_state = self.get_solver_state(request)
            f = request.json_body['f']
    
            solver_state.new_point(f)
            return self.return_new_data(request)    
        return ajax_error_catch(go)

    def ajax_solver_reset(self, request):
        def go():
            self.reset(request)
            return self.return_new_data(request)
        return ajax_error_catch(go)

    # TODO: catch errors when generating images
    def image(self, request):
        """ Returns an image """
        def go():
            solver_state = self.get_solver_state(request)
            ndp = solver_state.ndp
            ndp = ndp.abstract()
            model_name = self.get_model_name(request)

            # TODO: find a better way
            setattr(ndp, '_xxx_label', model_name)
            gg = gvgen_from_ndp(ndp, STYLE_GREENREDSYM)
            png, _pdf = png_pdf_from_gg(gg)
            return response_data(request=request, data=png, content_type='image/png')
        return png_error_catch(go, request)

def ajax_error_catch(f, quiet=(DPSyntaxError, DPSemanticError)):
    try:
        return f()
    except Exception as e:
        try:
            print(e)
        except UnicodeEncodeError:
            pass
        res = {}
        res['ok'] = False
        if isinstance(e, quiet):
            s = str(e)
        else:
            s = traceback.format_exc(e)
        res['error'] = s
        return res

def png_error_catch(f, request):
    try:
        return f()
    except Exception as e:
        try: 
            print(e)
        except UnicodeEncodeError:
            pass
        s = str(e)
    
        from PIL import Image
        # from PIL import ImageFont
        from PIL import ImageDraw 
        img = Image.new("RGB", (512, 512), "red")

        draw = ImageDraw.Draw(img)
#         font = ImageFont.truetype("sans-serif.ttf", 16)
        draw.text((0, 0), s, (255, 255, 255))  # , font=font)
        data = get_png(img)

        return response_data(request=request, data=data, content_type='image/png')

def get_png(image):
    """ Gets png data from PIL image """
    import tempfile
    with tempfile.NamedTemporaryFile(suffix='.png') as tf:
        fn = tf.name
        image.save(fn)
        with open(fn, 'rb') as f:
            data = f.read()
        return data


def create_alternative_urls(params, ndp):

    def make_url(faxes, raxes):
        faxes = ",".join(map(str, faxes))
        raxes = ",".join(map(str, raxes))
        model_name = params['model_name']
        return '/solver/%s/%s/%s/' % (model_name, faxes, raxes)

    # let's create the urls for different options
    fnames = ndp.get_fnames()
    rnames = ndp.get_rnames()

    fun_alternatives = []
    for option in itertools.permutations(range(len(fnames)), 2):
        url = make_url(faxes=option, raxes=params['res_axes'])
        desc = "%s vs %s" % (fnames[option[0]], fnames[option[1]])
        fun_alternatives.append({'url':url, 'desc':desc})

    res_alternatives = []
    for option in itertools.permutations(range(len(rnames)), 2):
        url = make_url(faxes=params['fun_axes'], raxes=option)
        desc = "%s vs %s" % (rnames[option[0]], rnames[option[1]])
        res_alternatives.append({'url':url, 'desc':desc})

    return fun_alternatives, res_alternatives
