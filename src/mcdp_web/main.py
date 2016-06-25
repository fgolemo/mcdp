from contracts import contract
from mcdp_library import MCDPLibrary
from mcdp_library.utils import locate_files
from mcdp_library.utils.dir_from_package_nam import dir_from_package_name
from mcdp_web.editor.app_editor import AppEditor
from mcdp_web.editor_fancy.app_editor_fancy_generic import AppEditorFancyGeneric
from mcdp_web.interactive.app_interactive import AppInteractive
from mcdp_web.qr.app_qr import AppQR
from mcdp_web.solver.app_solver import AppSolver
from mcdp_web.solver2.app_solver2 import AppSolver2
from mcdp_web.visualization.app_visualization import AppVisualization
from mocdp.exceptions import DPSemanticError, DPSyntaxError
from pyramid.config import Configurator
from pyramid.httpexceptions import HTTPFound
from quickapp import QuickAppBase
from wsgiref.simple_server import make_server
import os


__all__ = [
    'mcdp_web_main',
]


class WebApp(AppEditor, AppVisualization, AppQR, AppSolver, AppInteractive,
              AppSolver2, AppEditorFancyGeneric):

    def __init__(self, dirname):
        self.dirname = dirname
        self.libraries = load_libraries(self.dirname)
        logger.info('Found %d libraries underneath %r.' % (len(self.libraries), self.dirname))

        AppEditor.__init__(self)
        AppVisualization.__init__(self)
        AppQR.__init__(self)
        AppSolver.__init__(self)
        AppInteractive.__init__(self)
        # AppEditorFancy.__init__(self)
        AppSolver2.__init__(self)
        AppEditorFancyGeneric.__init__(self)

        # name -> dict(desc: )
        self.views = {}

        for x in ['syntax',
                # put in this order
                'ndp_graph',
                'dp_graph', 'ndp_repr',
                # XXX: put editor_fancy before editor
                'edit_fancy',
                'edit',
                'solver']:
            self.add_model_view(x, x)

    def add_model_view(self, name, desc):
        self.views[name] = dict(desc=desc)

    def _get_views(self):
        return sorted(self.views)

    def get_current_library_name(self, request):
        library_name = str(request.matchdict['library'])  # unicod
        return library_name

    def get_library(self, request):
        library_name = self.get_current_library_name(request)
        return self.libraries[library_name]['library']

    def list_of_models(self, request):
        l = self.get_library(request)
        return l.get_models()
    
    @contract(returns='list(str)')
    def list_libraries(self):
        """ Returns the list of libraries """
        return sorted(self.libraries)

    def view_index(self, request):  # @UnusedVariable
        return {}

    def view_list(self, request):
        models = self.list_of_models(request)
        return {
            'models': sorted(models),
            'navigation': self.get_navigation_links(request),
        }

    def view_list_libraries(self, request):  # @UnusedVariable
        libraries = self.list_libraries()
        return {'libraries': sorted(libraries)}


    def _refresh_library(self, _request):
        # nuclear option
        self.libraries = load_libraries(self.dirname)

        for l in [_['library'] for _ in self.libraries.values()]:
            l.delete_cache()

    def view_refresh_library(self, request):
        """ Refreshes the current library (if external files have changed) 
            then reloads the current url. """
        self._refresh_library(request)
        raise HTTPFound(request.referrer)

    def view_exception(self, exc, _request):
        import traceback

        compact = (DPSemanticError, DPSyntaxError)

        if isinstance(exc, compact):
            s = str(exc)
        else:
            s = traceback.format_exc(exc)
        s = s.decode('utf-8')
        print(s)
        return {'exception': s}
    
    def view_docs(self, request):
        docname = str(request.matchdict['document'])  # unicode

        # from pkg_resources import resource_filename  # @UnresolvedImport

        package = dir_from_package_name('mcdp_data')
        docs = os.path.join(package, 'docs')
        f = os.path.join(docs, '%s.md' % docname)
        import codecs
        data = codecs.open(f, encoding='utf-8').read()
        import markdown  # @UnresolvedImport

        extensions = [
            'markdown.extensions.smarty',
            'markdown.extensions.toc',
            'markdown.extensions.attr_list',
            # 'markdown.extensions.extra',
            'markdown.extensions.fenced_code',
            'markdown.extensions.admonition',
            'markdown.extensions.tables',
        ]
        html = markdown.markdown(data, extensions)
        # print html
        return {'contents': html}

    # This is where we keep all the URLS
    def get_lmv_url(self, library, model, view):
        url = '/libraries/%s/models/%s/views/%s/' % (library, model, view)
        return url

    def get_lib_template_view_url(self, library, template, view):
        url = '/libraries/%s/templates/%s/views/%s/' % (library, template, view)
        return url


    def get_model_name(self, request):
        model_name = str(request.matchdict['model_name'])  # unicod
        return model_name

    def get_current_view(self, request):
        url = request.url
        for x in self._get_views():
            if '/' + x + '/' in url:
                return x
        assert False, request.url

    def get_navigation_links(self, request):
        """ Pass this as "navigation" to the page. """

        if 'model_name' in request.matchdict:
            current_model = self.get_model_name(request)
            current_view = self.get_current_view(request)
        else:
            current_model = None
            current_view = None

        if 'template_name' in request.matchdict:
            current_template = str(request.matchdict['template_name'])
        else:
            current_template = None

        if 'poset_name' in request.matchdict:
            current_poset = str(request.matchdict['poset_name'])
        else:
            current_poset = None

        if 'value_name' in request.matchdict:
            current_value = str(request.matchdict['value_name'])
        else:
            current_value = None


        current_library = self.get_current_library_name(request)
        
        d = {}
        
        models = self.list_of_models(request)
        
        d['current_library'] = current_library
        d['current_template'] = current_template
        d['current_poset'] = current_poset
        d['current_view'] = current_view
        d['current_model'] = current_model

        d['models'] = []
        for m in models:
            is_current = m == current_model

            url = self.get_lmv_url(library=current_library,
                                   model=m,
                                   view='syntax')

            name = "Model %s" % m
            desc = dict(name=name, url=url, current=is_current)
            d['models'].append(desc)

        library = self.get_library(request)

        templates = library.list_templates()
        d['templates'] = []
        for t in templates:
            is_current = (t == current_template)

            url = self.get_lib_template_view_url(library=current_library,
                                                 template=t,
                                                 view='edit_fancy')  # XXX

            name = "Template %s" % t
            desc = dict(name=name, url=url, current=is_current)
            d['templates'].append(desc)

        posets = library.list_posets()
        d['posets'] = []
        for p in posets:
            is_current = (p == current_poset)
            url = '/libraries/%s/posets/%s/views/edit_fancy/' % (current_library, p)
            name = "Poset %s" % p
            desc = dict(name=name, url=url, current=is_current)
            d['posets'].append(desc)

        values = library.list_values()
        d['values'] = []
        for v in values:
            is_current = (v == current_value)
            url = '/libraries/%s/values/%s/views/edit_fancy/' % (current_library, v)
            name = "Value %s" % v
            desc = dict(name=name, url=url, current=is_current)
            d['values'].append(desc)


        d['views'] = []
        views = self._get_views()
        for v in views:
            is_current = v == current_view

            url = self.get_lmv_url(library=current_library,
                                   model=current_model,
                                   view=v)

            name = v  # XXX
            desc = dict(name=name, url=url, current=is_current)
            d['views'].append(desc)

        libraries = self.list_libraries()

        d['libraries'] = []
        for l in libraries:
            is_current = l == current_library
            url = '/libraries/%s/list' % l
            name = "Library %s" % l
            desc = dict(name=name, url=url, current=is_current)
            d['libraries'].append(desc)

        return d


    def serve(self):
        config = Configurator()
        config.add_static_view(name='static', path='static')
        config.include('pyramid_jinja2')

        AppEditor.config(self, config)
        AppVisualization.config(self, config)
        AppQR.config(self, config)
        AppSolver.config(self, config)
        AppInteractive.config(self, config)
        AppEditorFancyGeneric.config(self, config)

        AppSolver2.config(self, config)

        config.add_route('index', '/')
        config.add_view(self.view_index, route_name='index', renderer='index.jinja2')

        config.add_route('list_libraries', '/list')
        config.add_view(self.view_list_libraries, route_name='list_libraries', renderer='list_libraries.jinja2')

        config.add_route('list', '/libraries/{library}/list')
        config.add_view(self.view_list, route_name='list', renderer='list_models.jinja2')

        config.add_route('docs', '/docs/{document}/')
        config.add_view(self.view_docs, route_name='docs', renderer='language.jinja2')

        config.add_route('empty', '/empty')
        config.add_view(self.view_index, route_name='empty', renderer='empty.jinja2')

        config.add_route('refresh_library', '/libraries/{library}/refresh_library')
        config.add_view(self.view_refresh_library, route_name='refresh_library')

        config.add_view(self.view_exception, context=Exception, renderer='exception.jinja2')

        app = config.make_wsgi_app()
        server = make_server('0.0.0.0', 8080, app)
        server.serve_forever()


def load_libraries(dirname):
    """ Returns a dictionary
            
            library_name -> {'path': ...}
    """
    libraries = locate_files(dirname, "*.mcdplib",
                             followlinks=False,
                             include_directories=True,
                             include_files=False)
    res = {}
    for path in libraries:
        library_name = os.path.splitext(os.path.basename(path))[0]

        l = MCDPLibrary()
        cache_dir = os.path.join(path, '_mcdpweb_cache')
        l.use_cache_dir(cache_dir)
        l.add_search_dir(path)

        res[library_name] = dict(path=path, library=l)
    return res

from mocdp import logger

class MCDPWeb(QuickAppBase):
    """ Runs the MCDP web interface. """

    def define_program_options(self, params):
        params.add_string('dir', default=None, short='-d',
                           help='Library directories containing models.')

    def go(self):
        options = self.get_options()
        dirname = options.dir
        if dirname is None:
            package = dir_from_package_name('mcdp_data')
            libraries = os.path.join(package, 'libraries')
            msg = ('Command "-d" not passed, so I will open the default libraries '
                   'shipped with PyMCDP.')
            logger.info(msg)
            dirname = libraries

        wa = WebApp(dirname)
        msg = """Welcome to PyMCDP!
        
To access the interface, open your browser at the address
    
    http://127.0.0.1:8080/
    
Use Chrome, Firefox, or Opera - Internet Explorer is not supported.
"""
        logger.info(msg)
        wa.serve()

mcdp_web_main = MCDPWeb.get_sys_main()


