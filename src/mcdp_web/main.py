from mcdp_library.library import MCDPLibrary
from pyramid.config import Configurator
from pyramid.httpexceptions import HTTPFound
from quickapp.quick_app_base import QuickAppBase
from wsgiref.simple_server import make_server
from mcdp_web.app_editor import AppEditor
from mcdp_web.app_qr import AppQR
from mcdp_web.app_visualization import AppVisualization
from mcdp_web.app_solver import AppSolver
from pyramid.response import Response


__all__ = ['mcdp_web_main']


class WebApp(AppEditor, AppVisualization, AppQR, AppSolver):
    def __init__(self, dirname):
        self.dirname = dirname

        self.library = None

        AppEditor.__init__(self)
        AppVisualization.__init__(self)
        AppQR.__init__(self)
        AppSolver.__init__(self)

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

    def _refresh_library(self):
        l = self.get_library()
        l.delete_cache()
        self.library = None
        self.appqr_reset()


    def view_refresh_library(self, request):
        """ Refreshes the current library (if external files have changed) 
            then reloads the current url. """
        self._refresh_library()
        raise HTTPFound(request.referrer)

    def view_exception(self, exc, request):
        import traceback
        s = traceback.format_exc(exc)
        s = s.decode('utf-8')
        print(s)
        return {'exception': s}

    def serve(self):
        config = Configurator()
        config.add_static_view(name='static', path='static')
        config.include('pyramid_jinja2')

        AppEditor.config(self, config)
        AppVisualization.config(self, config)
        AppQR.config(self, config)
        AppSolver.config(self, config)

        config.add_route('list', '/')
        config.add_view(self.view_list, route_name='list', renderer='list.jinja2')

        config.add_route('empty', '/empty')
        config.add_view(self.view_index, route_name='empty', renderer='empty.jinja2')

        config.add_route('refresh_library', '/refresh_library')
        config.add_view(self.view_refresh_library, route_name='refresh_library')

        config.add_view(self.view_exception, context=Exception, renderer='exception.jinja2')

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

