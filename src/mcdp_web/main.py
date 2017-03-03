# -*- coding: utf-8 -*-
from collections import OrderedDict
import os
import sys
import time
import urlparse
from wsgiref.simple_server import make_server

from contracts import contract
from contracts.utils import indent
import pyramid
from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.config import Configurator
from pyramid.httpexceptions import HTTPFound
from pyramid.renderers import JSONP
from pyramid.response import Response
from quickapp import QuickAppBase

from mcdp import logger
from mcdp.exceptions import DPSemanticError, DPSyntaxError
from mcdp_docs.pipeline import render_complete
from mcdp_library import MCDPLibrary
from mcdp_library.utils import dir_from_package_name
from mcdp_shelf.shelves import find_shelves
from mcdp_user_db.userdb import UserDB
from mcdp_utils_misc import duration_compact, natural_sorted

from .confi import describe_mcdpweb_params, parse_mcdpweb_params_from_dict
from .editor_fancy import AppEditorFancyGeneric
from .images.images import WebAppImages, get_mime_for_format
from .interactive.app_interactive import AppInteractive
from .qr.app_qr import AppQR
from .resource_tree import MCDPResourceRoot, ResourceLibraries,\
    ResourceLibrary, get_from_context
from .resource_tree import ResourceShelves,\
    ResourceShelvesShelfUnsubscribe, ResourceShelvesShelfSubscribe,\
    ResourceShelvesShelf, ResourceExceptionsFormatted, ResourceExceptionsJSON
from .security import AppLogin
from .sessions import Session
from .solver.app_solver import AppSolver
from .solver2.app_solver2 import AppSolver2
from .status import AppStatus
from .utils0 import add_std_vars_context
from .visualization.app_visualization import AppVisualization
from mcdp_web.resource_tree import ResourceLibraryRefresh, ResourceRefresh,\
    ResourceExit, ResourceLibraryDocRender, context_get_library,\
    ResourceLibraryAsset


__all__ = [
    'mcdp_web_main',
    'app_factory',
]



class WebApp(AppVisualization, AppStatus,
             AppQR, AppSolver, AppInteractive,
             AppSolver2, AppEditorFancyGeneric, WebAppImages,
             AppLogin):
    singleton = None
    def __init__(self, options):
        self.options = options
        WebApp.singleton = self
        
        dirname = options.libraries
        if dirname is None:
            package = dir_from_package_name('mcdp_data')
            default_libraries = os.path.join(package, 'libraries')
            msg = ('Option "-d" not passed, so I will open the default libraries '
                   'shipped with PyMCDP. These might not be writable depending on your setup.')
            logger.info(msg)
            dirname = default_libraries


        self.dirname = dirname
 
        AppVisualization.__init__(self)
        AppQR.__init__(self)
        AppSolver.__init__(self)
        AppInteractive.__init__(self)
        AppSolver2.__init__(self)
        AppEditorFancyGeneric.__init__(self)
        WebAppImages.__init__(self)

        # name -> dict(desc: )
        self.views = {}
        self.exceptions = []
        
        self.add_model_view('syntax', 'Source code display')
        self.add_model_view('edit_fancy', 'Editor')
        # self.add_model_view('edit', 'Simple editor for IE')
        self.add_model_view('solver2', desc='Solver interface')
        self.add_model_view('ndp_graph', 'NDP Graph representation')
        self.add_model_view('ndp_repr', 'NDP Text representation')
        self.add_model_view('dp_graph', 'DP graph representation')
        self.add_model_view('dp_tree', 'DP tree representation')
        self.add_model_view('images', 'Other image representations')
        self.add_model_view('solver', 'Graphical solver [experimental]')
        
        # csfr_token -> Session
        self.sessions = OrderedDict()
        
        # str -> Shelf
        self.all_shelves = OrderedDict()
        
        dir_shelves = find_shelves(self.dirname)
        self.all_shelves.update(dir_shelves)
        
        if self.options.users is None:
            self.options.users = 'tmp-user-db'
            os.makedirs(self.options.users)

        if self.options.users is not None:
            self.user_db = UserDB(self.options.users)            
            user_shelves = find_shelves(self.options.users)
            self.all_shelves.update(user_shelves)
        
        for sname, shelf in self.all_shelves.items():
            print('init: Shelf %s' % sname)

    def add_model_view(self, name, desc):
        self.views[name] = dict(desc=desc, order=len(self.views))

    def get_session(self, request):
        token = request.session.get_csrf_token()
        if not token in self.sessions:
            print('creating new session for token %r' % token)
            self.sessions[token] = Session(request, shelves_all=self.all_shelves)
        session = self.sessions[token]
        session.set_last_request(request)
        return session
    
    def _get_views(self):
        return sorted(self.views, key=lambda _:self.views[_]['order'])

    def get_current_library_name(self, request, context=None):
        if context is None:
            return self.get_session(request).get_current_library_name()
        else:
            rlibrary = get_from_context(ResourceLibrary, context)
            return rlibrary.name
    
    def get_library(self, request, context=None):
        session = self.get_session(request)
        if context is None:
            return session.get_library()
        else:
            rlibrary = get_from_context(ResourceLibrary, context)
            if rlibrary is not None:
                current_library = rlibrary.name
                library = session.libraries[current_library]['library']
            else:
                current_library = None
                library = None
            return library

    def list_of_models(self, request):
        l = self.get_library(request)
        return l.get_models()
    
    @add_std_vars_context
    def view_dummy(self, context, request):  # @UnusedVariable
        return {}
 
    @add_std_vars_context
    def view_shelves_index(self, context, request):# @UnusedVariable
        return {}

    @add_std_vars_context
    def view_shelf(self, context, request):# @UnusedVariable
        sname = context.name
        session = self.get_session(request)
        shelf = session.shelves_available[sname]
        desc_long_md = shelf.get_desc_long()
        if desc_long_md is None:
            desc_long = ''
        else:
            library = MCDPLibrary()
            desc_long = render_complete(library, desc_long_md, raise_errors=True, realpath=sname, do_math=False)
        res = {
            'shelf': shelf, 
            'sname': sname, 
            'desc_long': unicode(desc_long, 'utf8'),
        }
        return res
    
    @add_std_vars_context 
    def view_shelves_subscribe(self, context, request):  # @UndefinedVariable
        sname = context.name
        session = self.get_session(request)
        print('subscribe %r' % sname)
        user = session.get_user()
        if not sname in user.subscriptions:
            user.subscriptions.append(sname)
            session.save_user()
            session.recompute_available()
        raise HTTPFound(request.referrer)
    
    @add_std_vars_context 
    def view_shelves_unsubscribe(self, context, request):  # @UndefinedVariable
        sname = context.name
        session = self.get_session(request)
        print('unsubscribe %r' % sname)
        user = session.get_user()
        if sname in user.subscriptions:
            user.subscriptions.remove(sname)
            session.save_user()
            session.recompute_available()
        raise HTTPFound(request.referrer)

    def refresh_library(self, request):
        # nuclear option
        session = self.get_session(request)
        session.refresh_libraries()

    def view_refresh_library(self, context, request):  # @UnusedVariable
        """ Refreshes the current library (if external files have changed) 
            then reloads the current url. """
#         self._refresh_library(request) 
        # Note this currently is equivalent to global refresh
        return self.view_refresh(request);

    def view_refresh(self, context, request):  # @UnusedVariable
        """ Refreshes all """
        self.refresh_library(request)
        raise HTTPFound(request.referrer)

    def view_not_found(self, request):
        request.response.status = 404
        url = request.url
        referrer = request.referrer
        self.exceptions.append('Path not found.\n url: %s\n ref: %s' % (url, referrer))
        res = {'url': url, 'referrer': referrer}
        
        res['root'] =  self.get_root_relative_to_here(request)
        return res

    @add_std_vars_context
    def view_exceptions_occurred(self, context, request):  # @UnusedVariable
        exceptions = []
        for e in self.exceptions:
            u = unicode(e, 'utf-8')
            exceptions.append(u)
        return {'exceptions': exceptions}

    def view_exception(self, exc, request):
        request.response.status = 500  # Internal Server Error

        import traceback
        compact = (DPSemanticError, DPSyntaxError)
        if isinstance(exc, compact):
            s = exc.__str__()
        else:
            s = traceback.format_exc(exc)

        url = request.url
        referrer = request.referrer
        n = 'Error during serving this URL:'
        n += '\n url: %s' % url
        n += '\n referrer: %s' % referrer
        ss = traceback.format_exc(exc)
        n += '\n' + indent(ss, '| ')
        self.exceptions.append(n)

#         session = self.get_session(request)
#         
#         if request.matchdict is not None and  'library' in request.matchdict:
#             library = self.get_current_library_name(request)
#             url_refresh = self.make_relative(request, '/libraries/%s/refresh_library' % library)
#         else:
#             url_refresh = None
#         
        u = unicode(s, 'utf-8')
        logger.error(u)
        res = {
            'exception': u,
            # 'url_refresh': url_refresh,
            'root': self.get_root_relative_to_here(request)
        }  
        return res
    
    def png_error_catch2(self, request, func):
        """ func is supposed to return an image response.
            If it raises an exception, we create
            an image with the error and then we add the exception
            to the list of exceptions.
            
             """
        try:
            return func()
        except Exception as e:
            import traceback
            s = traceback.format_exc(e)

            try:
                logger.error(s)
            except UnicodeEncodeError:
                pass

            s = str(s)
            url = request.url
            referrer = request.referrer
            n = 'Error during rendering an image.'
            n+= '\n url: %s' % url
            n+= '\n referrer: %s' % referrer
            n += '\n' + indent(s, '| ')
            self.exceptions.append(n)
            from mcdp_web.utils.image_error_catch_imp import response_image
            return response_image(request, s) 

    # This is where we keep all the URLS
    def make_relative(self, request, url):
        if not url.startswith('/'):
            msg = 'Expected url to start with /: %r' % url
            raise ValueError(msg)
        root = self.get_root_relative_to_here(request)
        comb = root + url
        
        # note: fails for trailing /
#         comb2 = os.path.normpath(comb)
#         print('comb %s -> %s' %(comb, comb2))
        return comb
    
    def get_lmv_url2(self, library, model, view, request):
        url0 = '/libraries/%s/models/%s/views/%s/' % (library, model, view)
        return self.make_relative(request, url0)
    
    def get_lvv_url2(self, library, value, view, request):
        url0 = '/libraries/%s/values/%s/views/%s/' % (library, value, view)
        return self.make_relative(request, url0)

    def get_ltv_url2(self, library, template, view, request):
        url0='/libraries/%s/templates/%s/views/%s/' % (library, template, view)
        return self.make_relative(request, url0)

    def get_lpv_url2(self, library, poset, view, request):
        url0 = '/libraries/%s/posets/%s/views/%s/' % (library, poset, view)
        return self.make_relative(request, url0)

    def get_glmv_url2(self, library, url_part, model, view, request):
        url0 = '/libraries/%s/%s/%s/views/%s/' % (library, url_part, model, view)
        return self.make_relative(request, url0)
    
    def get_lib_template_view_url2(self, library, template, view, request):
        url0 = '/libraries/%s/templates/%s/views/%s/' % (library, template, view)
        return self.make_relative(request, url0)

    def get_root_relative_to_here(self, request):
        if request is None:
            return ''
        else:
            path = urlparse.urlparse(request.url).path
            r = os.path.relpath('/', path)
            return r
        
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
        current_thing = None

        if 'model_name' in request.matchdict:
            current_thing = current_model = self.get_model_name(request)
            current_view = self.get_current_view(request)
        else:
            current_model = None
            current_view = None

        if 'template_name' in request.matchdict:
            current_thing = current_template = str(request.matchdict['template_name'])
        else:
            current_template = None

        if 'poset_name' in request.matchdict:
            current_thing = current_poset = str(request.matchdict['poset_name'])
        else:
            current_poset = None

        if 'value_name' in request.matchdict:
            current_thing = current_value = str(request.matchdict['value_name'])
        else:
            current_value = None

        if 'library' in request.matchdict:
            current_library = self.get_current_library_name(request)
            library = self.get_library(request)
        else:
            current_library = None
            library = None

        d = {}

        d['current_thing'] = current_thing
        d['current_library'] = current_library
        d['current_template'] = current_template
        d['current_poset'] = current_poset
        d['current_model'] = current_model
        d['current_view'] = current_view

        make_relative = lambda _: self.make_relative(request, _)

        if library is not None:
            documents = library._list_with_extension(MCDPLibrary.ext_doc_md)

            d['documents'] = []
            for id_doc in documents:
                url = make_relative('/libraries/%s/%s.html' % (current_library, id_doc))
                desc = dict(id=id_doc,id_document=id_doc, name=id_doc, url=url, current=False)
                d['documents'].append(desc)
    
            d['models'] = []
            
            VIEW_EDITOR = 'edit_fancy'
            
            models = self.list_of_models(request)
            for m in natural_sorted(models):
                is_current = m == current_model
    
                url = self.get_lmv_url2(library=current_library,
                                       model=m,
                                       view='syntax', request=request)
                url_edit =  self.get_lmv_url2(library=current_library,
                                       model=m,
                                       view=VIEW_EDITOR, request=request)
                name = "Model %s" % m
                desc = dict(id=m, id_ndp=m, name=name, url=url, url_edit=url_edit, current=is_current)
                d['models'].append(desc)
    
    
            templates = library.list_templates()
            d['templates'] = []
            for t in natural_sorted(templates):
                is_current = (t == current_template)
    
                url = self.get_lib_template_view_url2(library=current_library,
                                                     template=t,
                                                     view='syntax', request=request) 
                url_edit = self.get_lib_template_view_url2(library=current_library,
                                                     template=t,
                                                     view=VIEW_EDITOR,request= request)  
    
                name = "Template: %s" % t
                desc = dict(id=t, name=name, url=url, current=is_current, url_edit=url_edit)
                d['templates'].append(desc)
    
            posets = library.list_posets()
            d['posets'] = []
            for p in natural_sorted(posets):
                is_current = (p == current_poset)
                url = self.get_lpv_url2(library=current_library,
                                       poset=p,
                                       view='syntax', request=request)
                url_edit = self.get_lpv_url2(library=current_library,
                                       poset=p,
                                       view=VIEW_EDITOR,request= request)
                name = "Poset: %s" % p
                desc = dict(id=p, name=name, url=url, current=is_current, url_edit=url_edit)
                d['posets'].append(desc)
    
            values = library.list_values()
            d['values'] = []
            for v in natural_sorted(values):
                is_current = (v == current_value)
                url = '/libraries/%s/values/%s/views/syntax/' % (current_library, v)
                url_edit = '/libraries/%s/values/%s/views/%s/' % (current_library, v, VIEW_EDITOR)
                name = "Value: %s" % v
                desc = dict(id=v,name=name, url=url, current=is_current, url_edit=url_edit)
                d['values'].append(desc)
    
    
            d['views'] = []
            views = self._get_views()
            for v in views:
                view = self.views[v]
                is_current = v == current_view
    
                url = self.get_lmv_url2(library=current_library,
                                       model=current_model,
                                       view=v, request=request)
    
                name = "View: %s" % view['desc']
                desc = dict(name=name, url=url, current=is_current)
                d['views'].append(desc)
        # endif library not None
        session = self.get_session(request)
        libraries = session.list_libraries()

        # just the list of names
        d['libraries'] = []
        libname2desc = {}
        for l in natural_sorted(libraries):
            is_current = l == current_library
            url = make_relative('/libraries/%s/' % l)
            #name = "Library: %s" % l
            name = l
            desc = dict(id=l,name=name, url=url, current=is_current)
            libname2desc[l] =desc
            d['libraries'].append(desc)

        indexed = session.get_libraries_indexed_by_dir()
        indexed = [(sup, [libname2desc[_] for _ in l]) 
                   for sup, l in indexed]
        
        # for sup, libraries in libraries_indexed
        #   for l in libraries
        #      l['name'], l['url']
        d['libraries_indexed'] = indexed
        
        return d
    
    
    @add_std_vars_context
    def view_library_doc(self, context, request):
        """ '/libraries/{library}/{document}.html' """
        # f['data'] not utf-8
        # reopen as utf-8
        document = context.name
        html = self._render_library_doc(context, request, document)
        # we work with utf-8 strings
        assert isinstance(html, str)
        # but we need to convert to unicode later
        html = unicode(html, 'utf-8')
        res = {}
        res['contents'] = html
        res['title'] = document
        res['print'] = bool(request.params.get('print', False))
        return res

    @contract(returns=str)
    def _render_library_doc(self, context, request, document):
        import codecs
        l = context_get_library(context, request)

        strict = int(request.params.get('strict', '0'))

        filename = '%s.%s' % (document, MCDPLibrary.ext_doc_md)
        f = l._get_file_data(filename)
        realpath = f['realpath']
        # read unicode
        data_unicode = codecs.open(realpath, encoding='utf-8').read()
        data_str = data_unicode.encode('utf-8')
        raise_errors = bool(strict)
        html = render_complete(library=l, s=data_str, realpath=realpath, raise_errors=raise_errors)
        return html

    def view_library_asset(self, context, request):
        library = context_get_library(context, request)
        asset = os.path.splitext(context.name)[0]
        ext = os.path.splitext(context.name)[1][1:]
        filename = '%s.%s' % (asset, ext)
        f = library._get_file_data(filename)
        data = f['data']
        content_type = get_mime_for_format(ext)
        from mcdp_web.utils.response import response_data
        return response_data(request, data, content_type)

    def exit(self, context, request):  # @UnusedVariable
        sys.exit(0)
        setattr(self.server, '_BaseServer__shutdown_request', True)
        howlong = duration_compact(self.get_uptime_s())
        return "Bye. Uptime: %s." % howlong

    def get_uptime_s(self):
        return time.time() - self.time_start
    
    def serve(self, port):
        app = self.get_app()
        self.server = make_server('0.0.0.0', port, app)
        self.server.serve_forever()
        
    def get_app(self): 
        self.time_start = time.time()
        from pyramid.session import SignedCookieSessionFactory
        
        secret = 'itsasecreet' # XXX
        
        self.my_session_factory = SignedCookieSessionFactory(secret+'sign')

        config = Configurator(root_factory=MCDPResourceRoot)
        config.set_session_factory(self.my_session_factory)

        # config.include('pyramid_debugtoolbar')

        authn_policy = AuthTktAuthenticationPolicy(secret+'authn', hashalg='sha512')
        authz_policy = ACLAuthorizationPolicy()
        config.set_authentication_policy(authn_policy)
        config.set_authorization_policy(authz_policy)
        config.set_default_permission('access')

        config.add_renderer('jsonp', JSONP(param_name='callback'))

        config.add_static_view(name='static', path='static', cache_max_age=3600)
        config.include('pyramid_jinja2')

        AppStatus.config(self, config)
        AppVisualization.config(self, config)
        AppQR.config(self, config)
        AppSolver.config(self, config)
        AppInteractive.config(self, config)
        AppEditorFancyGeneric.config(self, config)
        WebAppImages.config(self, config)
        AppLogin.config(self, config)
        AppSolver2.config(self, config)


        config.add_view(self.view_dummy, context=MCDPResourceRoot, renderer='index.jinja2')
        config.add_view(self.view_dummy, context=ResourceLibraries, renderer='list_libraries.jinja2')
        config.add_view(self.view_dummy, context=ResourceLibrary, renderer='library_index.jinja2')
        config.add_view(self.view_shelves_index, context=ResourceShelves, renderer='shelves_index.jinja2')
        config.add_view(self.view_shelf, context=ResourceShelvesShelf, renderer='shelf.jinja2')
        config.add_view(self.view_shelves_subscribe, context=ResourceShelvesShelfSubscribe)
        config.add_view(self.view_shelves_unsubscribe, context=ResourceShelvesShelfUnsubscribe)
        
        config.add_view(self.view_library_doc, 
                        context=ResourceLibraryDocRender,
                        renderer='library_doc.jinja2')

        config.add_view(self.view_library_asset, 
                        context=ResourceLibraryAsset)

        config.add_view(self.view_refresh_library, 
                        context=ResourceLibraryRefresh)
        config.add_view(self.view_refresh, 
                        context=ResourceRefresh)
        config.add_view(self.view_exception, 
                        context=Exception, 
                        renderer='exception.jinja2')

        config.add_view(self.exit, context=ResourceExit, renderer='json',
                        permission=pyramid.security.NO_PERMISSION_REQUIRED)

        config.add_view(self.view_exceptions_occurred, 
                        context=ResourceExceptionsJSON, 
                        renderer='json')
        config.add_view(self.view_exceptions_occurred, 
                        context=ResourceExceptionsFormatted, 
                        renderer='exceptions_formatted.jinja2')

        # mainly used for wget
        config.add_route('robots', '/robots.txt')
        def serve_robots(request):  # @UnusedVariable
            body = "User-agent: *\nDisallow:"
            return Response(content_type='text/plain', body=body)

        config.add_view(serve_robots, route_name='robots')

        config.add_notfound_view(self.view_not_found, renderer='404.jinja2')
        config.scan()

        app = config.make_wsgi_app()
        return app
    

    

class MCDPWeb(QuickAppBase):
    """ Runs the MCDP web interface. """

    def define_program_options(self, params):
        describe_mcdpweb_params(params)
        params.add_int('port', default=8080, help='Port to listen to.')
        
    def go(self):
        options = self.get_options()
        wa = WebApp(options)
        msg = """Welcome to PyMCDP!
        
To access the interface, open your browser at the address
    
    http://127.0.0.1:%s/
    
Use Chrome, Firefox, or Opera - Internet Explorer is not supported.
""" % options.port

        if options.delete_cache:
            logger.info('Deleting cache...')
            #wa._refresh_library(None)
        logger.info(msg)
        wa.serve(port=options.port)

def get_only_prefixed(settings, prefix):
    res = {}
    for k, v in settings.items():
        if k.startswith(prefix):
            k2 = k[len(prefix):]
            res[k2]= v
    return res
            
def app_factory(global_config, **settings):  # @UnusedVariable
    settings = get_only_prefixed(settings, 'mcdp_web.')
    #print('app_factory settings %s' % settings)
    options = parse_mcdpweb_params_from_dict(settings)
    
    wa = WebApp(options)
    app = wa.get_app()
    return app

mcdp_web_main = MCDPWeb.get_sys_main()

