from wsgiref.simple_server import make_server
from pyramid.config import Configurator
from pyramid.response import Response, FileResponse
from conf_tools.global_config import GlobalConfig
from quickapp.quick_app_base import QuickAppBase
from mcdp_library.library import MCDPLibrary
from pyramid.view import view_config
from mocdp.dp_report.html import ast_to_html

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

    def view_model_ndp_graph(self, request):
        model_name = str(request.matchdict['model_name'])  # unicod
        style = request.matchdict['style']

        from mocdp.dp_report.gg_ndp import gvgen_from_ndp
        from cdpview.plot import png_pdf_from_gg

        _, ndp = self.get_library().load_ndp(model_name)
        gg = gvgen_from_ndp(ndp, style)
        png, pdf = png_pdf_from_gg(gg)

        import tempfile
        with tempfile.NamedTemporaryFile(suffix='.png') as tf:
            fn = tf.name
            with open(fn, 'wb') as f:
                f.write(png)

            response = FileResponse(fn, request=request, content_type='image/png')

        return response

    def view_model_syntax(self, request):
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
                'realpath': realpath}

    def serve(self):
        config = Configurator()
        config.include('pyramid_jinja2')

        config.add_route('index', '/')
        config.add_view(self.view_index, route_name='index', renderer='index.jinja2')

        config.add_route('list', '/list')
        config.add_view(self.view_list, route_name='list', renderer='list.jinja2')

        config.add_route('empty', '/empty')
        config.add_view(self.view_index, route_name='empty', renderer='empty.jinja2')

        config.add_route('model_syntax', '/models/{model_name}/syntax')
        config.add_view(self.view_model_syntax, route_name='model_syntax',
                        renderer='model_syntax.jinja2')

        config.add_route('model_ndp_graph', '/models/{model_name}/ndp_graph/{style}')
        config.add_view(self.view_model_ndp_graph, route_name='model_ndp_graph')

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

