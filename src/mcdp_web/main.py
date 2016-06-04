from wsgiref.simple_server import make_server
from pyramid.config import Configurator
from pyramid.response import Response, FileResponse
from quickapp.quick_app_base import QuickAppBase
from mcdp_library.library import MCDPLibrary
from mocdp.dp_report.html import ast_to_html
from mocdp.exceptions import DPSemanticError, DPSyntaxError
from pyramid.request import Request
from pyramid.renderers import render_to_response
from mocdp.dp_report.gg_ndp import STYLE_GREENREDSYM
import os
from pyramid.httpexceptions import HTTPFound

__all__ = ['mcdp_web_main']

class WebApp():
    def __init__(self, dirname):
        self.dirname = dirname

        self.counter = 0
    
        self.library = None


    def get_library(self):
        if self.library is None:
            l = MCDPLibrary()
            l = l.add_search_dir(self.dirname)
            self.library = l
        return self.library

    def list_of_models(self):
        l = self.get_library()
        return l.get_models()

    def view_index(self, request):  # @UnusedVariable
        return {}

    def view_list(self, request):  # @UnusedVariable
        models = self.list_of_models()
        return {'models': sorted(models)}

    def view_model_ndp_graph_image(self, request):
        model_name = str(request.matchdict['model_name'])  # unicod
        style = request.matchdict['style']
        fileformat = request.matchdict['format']

        from mocdp.dp_report.gg_ndp import gvgen_from_ndp
        from cdpview.plot import png_pdf_from_gg

        _, ndp = self.get_library().load_ndp(model_name)
        gg = gvgen_from_ndp(ndp, style)
        png, pdf = png_pdf_from_gg(gg)

        if fileformat == 'pdf':
            return response_data(request=request, data=pdf, content_type='image/pdf')
        elif fileformat == 'png':
            return response_data(request=request, data=png, content_type='image/png')
        else:
            raise ValueError('No known format %r.' % fileformat)


    def view_model_ndp_graph(self, request):
        model_name = str(request.matchdict['model_name'])  # unicode
        models = self.list_of_models()
        
        return {'model_name': model_name,
                'models': models,
                'views': self._get_views(),
                'current_view': 'ndp_graph',
                'style': STYLE_GREENREDSYM}

    def view_model_ndp_repr(self, request):
        model_name = str(request.matchdict['model_name'])  # unicode
        models = self.list_of_models()
        _, ndp = self.get_library().load_ndp(model_name)
        ndp_string = ndp.__repr__()
        ndp_string = ndp_string.decode("utf8")

        return {'model_name': model_name,
                'models': models,
                'views': self._get_views(),
                'content': ndp_string,
                'current_view': 'ndp_repr'}


    def view_model_syntax(self, request):
        models = self.list_of_models()
        model_name = str(request.matchdict['model_name'])  # unicode

        filename = '%s.mcdp' % model_name
        l = self.get_library()
        f = l._get_file_data(filename)
        source_code = f['data']
        realpath = f['realpath']

        highlight = ast_to_html(source_code, complete_document=False)

        return {'source_code': source_code,
                'highlight': highlight,
                'model_name': model_name,
                'realpath': realpath,
                'models': models,
                'views': self._get_views(),
                'current_view': 'syntax'}

    def _get_views(self):
        return ['syntax', 'ndp_graph', 'ndp_repr']

    def view_edit_form(self, request):
        model_name = str(request.matchdict['model_name'])  # unicode

        filename = '%s.mcdp' % model_name
        l = self.get_library()
        f = l._get_file_data(filename)
        source_code = f['data']
        realpath = f['realpath']
        nrows = int(len(source_code.split('\n')) + 6)

        return {'source_code': source_code,
                'model_name': model_name,
                'realpath': realpath,
                'rows': nrows,
                'error': None}


    def view_edit_submit(self, request):
        model_name = str(request.matchdict['model_name'])  # unicode

        filename = '%s.mcdp' % model_name
        l = self.get_library()
        f = l._get_file_data(filename)
        realpath = f['realpath']

        data = str(request.params['source_code'])
        data = data.replace('\r', '')
        # validation:
        try:
            _parsed = l._actual_load(data, realpath=None)
        except (DPSemanticError, DPSyntaxError) as e:
            error = str(e)
            nrows = int(len(data.split('\n')) + 6)
            params = {'source_code': data,
                      'model_name': model_name,
                      'error': error,
                      'rows': nrows}

            return render_to_response('edit_form.jinja2',
                                      params, request=request)

        l.write_to_model(model_name, data)

        subreq = Request.blank('/models/%s/syntax' % model_name)
        response = request.invoke_subrequest(subreq)
        return response

    def view_new_model(self, request):
        model_name = str(request.matchdict['model_name'])  # unicode
        basename = model_name + '.mcdp'
        l = self.get_library()
        if l.file_exists(basename):
            error = 'File %r already exists.' % basename
            return render_to_response('error_model_exists.jinja2',
                                      {'error': error,
                                       'model_name': model_name}, request=request)

        else:
            source = "mcdp {\n\n}"
            filename = os.path.join(self.dirname, basename)
            with open(filename, 'w') as f:
                f.write(source)
            l._update_file(filename)

            return render_to_response('ok_model_created.jinja2',
                                      {'model_name': model_name}, request=request)

    def view_refresh_library(self, request):
        """ Refreshes the current library (if external files have changed) 
            then reloads the current url. """
        l = self.get_library()
        l.delete_cache()
        self.library = None
        raise HTTPFound(request.referrer)

    def serve(self):
        config = Configurator()
        config.add_static_view(name='static', path='static')
        config.include('pyramid_jinja2')

#         config.add_route('index', '/')
#         config.add_view(self.view_index, route_name='index', renderer='index.jinja2')

        config.add_route('list', '/')
        config.add_view(self.view_list, route_name='list', renderer='list.jinja2')

        config.add_route('empty', '/empty')
        config.add_view(self.view_index, route_name='empty', renderer='empty.jinja2')

        config.add_route('edit_form', '/edit/{model_name}')
        config.add_view(self.view_edit_form, route_name='edit_form',
                        renderer='edit_form.jinja2')

        config.add_route('edit_submit', '/edit_submit/{model_name}')
        config.add_view(self.view_edit_submit, route_name='edit_submit')

        config.add_route('model_syntax', '/models/{model_name}/syntax')
        config.add_view(self.view_model_syntax, route_name='model_syntax',
                        renderer='model_syntax.jinja2')

        config.add_route('model_ndp_graph', '/models/{model_name}/ndp_graph')
        config.add_view(self.view_model_ndp_graph, route_name='model_ndp_graph',
                        renderer='model_ndp_graph.jinja2')

        config.add_route('model_ndp_graph_image', '/models/{model_name}/ndp_graph/image/{style}.{format}')
        config.add_view(self.view_model_ndp_graph_image, route_name='model_ndp_graph_image')

        config.add_route('model_ndp_repr', '/models/{model_name}/ndp_repr')
        config.add_view(self.view_model_ndp_repr, route_name='model_ndp_repr',
                        renderer='model_generic_text_content.jinja2')

        config.add_route('new_model', '/new_model/{model_name}')
        config.add_view(self.view_new_model, route_name='new_model')

        config.add_route('refresh_library', '/refresh_library')
        config.add_view(self.view_refresh_library, route_name='refresh_library')

        app = config.make_wsgi_app()
        server = make_server('0.0.0.0', 8080, app)
        server.serve_forever()

class MCDPWeb(QuickAppBase):

    def define_program_options(self, params):
        params.add_string('dir', default='.', short='-d',
                           help='Library directories containing models.')

    def go(self):
        options = self.get_options()
        dirname = options.dir
        wa = WebApp(dirname)
        wa.serve()

mcdp_web_main = MCDPWeb.get_sys_main()



def response_data(request, data, content_type):
    import tempfile
    with tempfile.NamedTemporaryFile() as tf:
        fn = tf.name
        with open(fn, 'wb') as f:
            f.write(data)
        response = FileResponse(fn, request=request, content_type=content_type)

    return response
