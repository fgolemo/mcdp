# -*- coding: utf-8 -*-
from collections import OrderedDict
import datetime
import os
import sys
import time
import urlparse
from wsgiref.simple_server import make_server

from contracts import contract
from contracts.utils import indent
import git.cmd  # @UnusedImport
from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.config import Configurator
from pyramid.httpexceptions import HTTPFound
from pyramid.renderers import JSONP, render_to_response
from pyramid.response import Response
from pyramid.security import NO_PERMISSION_REQUIRED
from pyramid.session import SignedCookieSessionFactory
from quickapp import QuickAppBase

from mcdp import MCDPConstants
from mcdp import logger
from mcdp.exceptions import DPSemanticError, DPSyntaxError
from mcdp_docs import render_complete
from mcdp_library import MCDPLibrary
from mcdp_repo import MCDPGitRepo, MCDPythonRepo
from mcdp_shelf import PRIVILEGE_ACCESS, PRIVILEGE_READ, PRIVILEGE_SUBSCRIBE
from mcdp_user_db import UserDB,  UserInfo
from mcdp_utils_misc import create_tmpdir,  duration_compact, dir_from_package_name

from .confi import describe_mcdpweb_params, parse_mcdpweb_params_from_dict
from .editor_fancy import AppEditorFancyGeneric
from .environment import Environment
from .environment import cr2e
from .images.images import WebAppImages, get_mime_for_format
from .interactive.app_interactive import AppInteractive
from .qr.app_qr import AppQR
from .resource_tree import MCDPResourceRoot, ResourceLibraries,\
    ResourceLibrary,  ResourceLibraryRefresh, ResourceRefresh,\
    ResourceExit, ResourceLibraryDocRender,\
    ResourceLibraryAsset, ResourceRobots, ResourceShelves,\
    ResourceShelvesShelfUnsubscribe, ResourceShelvesShelfSubscribe,\
    ResourceExceptionsFormatted, ResourceExceptionsJSON, ResourceShelf, ResourceLibrariesNewLibname,\
    Resource,\
    context_display_in_detail, ResourceShelfInactive, ResourceThingDelete, ResourceChanges, ResourceTree, ResourceThing
from .resource_tree import ResourceRepos, ResourceRepo
from .security import AppLogin, groupfinder
from .sessions import Session
from .solver.app_solver import AppSolver
from .solver2.app_solver2 import AppSolver2
from .status import AppStatus
from .utils.image_error_catch_imp import response_image
from .utils.response import response_data
from .utils0 import add_other_fields, add_std_vars_context
from .visualization.app_visualization import AppVisualization
from mcdp_shelf.access import PRIVILEGE_DISCOVER


__all__ = [
    'mcdp_web_main',
    'app_factory',
]


git.cmd.log.disabled = True


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
        
        if self.options.users is None:
            self.options.users = create_tmpdir('tmp-user-db')
            os.makedirs(self.options.users)

        self.repos = {}
        REPO_BUNDLED = 'bundled'
        REPO_USERS = 'global'
        if self.options.load_mcdp_data:
            if os.path.exists('.git'):
                logger.info('Loading mcdp_data repo as MCDPGitRepo')
                self.repos[REPO_BUNDLED] = MCDPGitRepo(where='.')
            else:
                logger.info('Loading mcdp_data repo as MCDPythonRepo')
                self.repos[REPO_BUNDLED] = MCDPythonRepo('mcdp_data')
        else:
            logger.info('Not loading mcdp_data')
            
        if self.options.users is not None:
            self.user_db = UserDB(self.options.users)            
            self.repos[REPO_USERS] = MCDPGitRepo(where=self.options.users)

        for id_repo, repo in self.repos.items():
            user_shelves = repo.get_shelves()
            logger.info('%s: %s' % (id_repo, sorted(user_shelves)))
            self.all_shelves.update(user_shelves)
        
    def add_model_view(self, name, desc):
        self.views[name] = dict(desc=desc, order=len(self.views))

    def get_session(self, request):
        token = request.session.get_csrf_token()
        if not token in self.sessions:
            # print('creating new session for token %r' % token)
            self.sessions[token] = Session(app=self, request=request, shelves_all=self.all_shelves)
        session = self.sessions[token]
        session.set_last_request(request)
        return session
    
    def _get_views(self):
        return sorted(self.views, key=lambda _:self.views[_]['order'])
       
    @add_std_vars_context
    @cr2e
    def view_dummy(self, e):  # @UnusedVariable
        return {}
    
    @add_std_vars_context
    @cr2e
    def view_index(self, e):
        return {
            'changes': self._get_changes(e),
        }
 
    @add_std_vars_context
    @cr2e
    def view_tree(self, e):
        root = MCDPResourceRoot(e.request)
        
        def get_pages(node, prefix):
            
            for child in node:
                yield "/".join(prefix + (child,))
                for _ in get_pages(node[child], prefix + (child,)):
                    yield _
                    
        pages = list(get_pages(node=root, prefix=()))
        pages = [(_, len(_.split('/'))) for _ in pages]
        return {'pages': pages}
        
    @add_std_vars_context
    @cr2e
    def view_shelf(self, e):
        desc_long_md = e.shelf.get_desc_long()
        if desc_long_md is None:
            desc_long = ''
        else:
            library = MCDPLibrary()
            desc_long = render_complete(library, desc_long_md, raise_errors=True, realpath=e.shelf_name, do_math=False)
        res = {
            'shelf': e.shelf, 
            'sname': e.shelf_name, 
            'desc_long': unicode(desc_long, 'utf8'),
        }
        return res
    
    @add_std_vars_context 
    @cr2e
    def view_shelves_subscribe(self, e):  
        if not e.shelf_name in e.user.subscriptions:
            e.user.subscriptions.append(e.shelf_name)
            e.session.save_user()
            e.session.recompute_available()
        raise HTTPFound(e.request.referrer)
    
    @cr2e
    def view_shelf_library_new(self, e):
        new_library_name = e.context.name
        url_edit = get_url_library(e, e.shelf_name, new_library_name)

        if new_library_name in e.shelf.libraries:
            error = 'The library "%s" already exists.' %new_library_name
            template = 'error_library_exists.jinja2'
            res = {
                'error': error,
                'library_name': new_library_name,
                'url_edit': url_edit,
            }
            add_other_fields(self, res, e.request, context=e.context)
            return render_to_response(template, res, request=e.request)
        else:
            # does not exist
            dirname = os.path.join(e.shelf.write_to, new_library_name + '.' + MCDPConstants.library_extension)
            if os.path.exists(dirname):
                logger.error('Directory %s already exists.' % dirname)
            else:
                os.makedirs(dirname)
                one = os.path.join(dirname, '.gitignore')
                with open(one, 'w') as f:
                    f.write("")
                    
                logger.info('Created library %r in %r' % (new_library_name, dirname))
            
            e.session.notify_created_library(e.shelf_name,new_library_name)
            raise HTTPFound(url_edit) 
         
    @cr2e
    def view_shelves_unsubscribe(self, e):
        sname = e.context.name
        #print('unsubscribe %r' % sname)
        if sname in e.user.subscriptions:
            e.user.subscriptions.remove(sname)
            e.session.save_user()
            e.session.recompute_available()
        raise HTTPFound(e.request.referrer)

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

    @cr2e
    def view_refresh(self, e): 
        """ Refreshes all """
        self.refresh_library(e.request) 
        if e.request.referrer is None:
            redirect = self.get_root_relative_to_here(e.request)
        else:
            redirect = e.request.referrer
        raise HTTPFound(redirect)

    @cr2e
    def view_not_found(self, e):
        e.request.response.status = 404
        url = e.request.url
        referrer = e.request.referrer
        #print('context: %s' % e.context)
        self.exceptions.append('Path not found.\n url: %s\n ref: %s' % (url, referrer))
        res = {
            'url': url,
             'referrer': referrer,
             'root': e.root,
             'static': e.root + '/static',
        }

        return res

    @add_std_vars_context
    @cr2e
    def view_exceptions_occurred(self, e):  # @UnusedVariable
        exceptions = []
        for e in self.exceptions:
            u = unicode(e, 'utf-8')
            exceptions.append(u)
        return {'exceptions': exceptions}

    @cr2e
    def view_exceptions_occurred_json(self, e):  # @UnusedVariable
        exceptions = []
        for e in self.exceptions:
            u = unicode(e, 'utf-8')
            exceptions.append(u)
        return {'exceptions': exceptions}

    def view_exception(self, exc, request):
        request.response.status = 500  # Internal Server Error

        if hasattr(request, 'context'):
            if isinstance(request.context, Resource):
                logger.debug(context_display_in_detail(request.context))
            
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
 
        u = unicode(s, 'utf-8')
        logger.error(u)
        root = self.get_root_relative_to_here(request)
        res = {
            'exception': u,
            # 'url_refresh': url_refresh,
            'root': root,
            'static': root + '/static'
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
            
            return response_image(request, s) 

    # This is where we keep all the URLS
    def make_relative(self, request, url):
        if not url.startswith('/'):
            msg = 'Expected url to start with /: %r' % url
            raise ValueError(msg)
        root = self.get_root_relative_to_here(request)
        comb = root + url
         
        return comb
    

    def get_root_relative_to_here(self, request):
        if request is None:
            return ''
        else:
            path = urlparse.urlparse(request.url).path
            r = os.path.relpath('/', path)
            return r


    @add_std_vars_context
    @cr2e
    def view_library_doc(self, e):
        """ '/libraries/{library}/{document}.html' """
        # f['data'] not utf-8
        # reopen as utf-8
        document = e.context.name
        html = self._render_library_doc(e.context, e.request, document)
        # we work with utf-8 strings
        assert isinstance(html, str)
        # but we need to convert to unicode later
        html = unicode(html, 'utf-8')
        res = {}
        res['contents'] = html
        res['title'] = document
        res['print'] = bool(e.request.params.get('print', False))
        return res

    @contract(returns=str)
    def _render_library_doc(self, context, request, document):
        import codecs
        e = Environment(context, request)

        strict = int(request.params.get('strict', '0'))

        filename = '%s.%s' % (document, MCDPConstants.ext_doc_md)
        f = e.library._get_file_data(filename)
        realpath = f['realpath']
        # read unicode
        data_unicode = codecs.open(realpath, encoding='utf-8').read()
        data_str = data_unicode.encode('utf-8')
        raise_errors = bool(strict)
        html = render_complete(library=e.library, s=data_str, realpath=realpath, raise_errors=raise_errors)
        return html

    @cr2e
    def view_library_asset(self, e):
        asset = os.path.splitext(e.context.name)[0]
        ext = os.path.splitext(e.context.name)[1][1:]
        filename = '%s.%s' % (asset, ext)
        f = e.library._get_file_data(filename)
        data = f['data']
        content_type = get_mime_for_format(ext)
        return response_data(e.request, data, content_type)

    @cr2e
    def exit(self, e):  # @UnusedVariable
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

        secret = 'itsasecreet' # XXX
        
        self.my_session_factory = SignedCookieSessionFactory(secret+'sign')

        config = Configurator(root_factory=MCDPResourceRoot)
        config.set_session_factory(self.my_session_factory)

        # config.include('pyramid_debugtoolbar')

        authn_policy = AuthTktAuthenticationPolicy(secret+'authn', hashalg='sha512', callback=groupfinder )
        authz_policy = ACLAuthorizationPolicy()
        config.set_authentication_policy(authn_policy)
        config.set_authorization_policy(authz_policy)
        config.set_default_permission(PRIVILEGE_ACCESS)

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

        config.add_view(self.view_index, context=MCDPResourceRoot, renderer='index.jinja2')
        config.add_view(self.view_dummy, context=ResourceLibraries, renderer='list_libraries.jinja2')
        config.add_view(self.view_dummy, context=ResourceRepos, renderer='repos.jinja2')
        
        config.add_view(self.view_dummy, context=ResourceLibrary, renderer='library_index.jinja2', permission=PRIVILEGE_READ)
        config.add_view(self.view_dummy, context=ResourceRepo, renderer='shelves_index.jinja2')
        config.add_view(self.view_dummy, context=ResourceShelves, renderer='shelves_index.jinja2') # same as above
        config.add_view(self.view_changes, context=ResourceChanges, renderer='changes.jinja2')
        config.add_view(self.view_tree, context=ResourceTree, renderer='tree.jinja2')
        
        config.add_view(self.view_shelf_library_new, context=ResourceLibrariesNewLibname)
        config.add_view(self.view_shelf, context=ResourceShelf, renderer='shelf.jinja2', permission=PRIVILEGE_DISCOVER)
        config.add_view(self.view_shelves_subscribe, context=ResourceShelvesShelfSubscribe, permission=PRIVILEGE_SUBSCRIBE)
        config.add_view(self.view_shelves_unsubscribe, context=ResourceShelvesShelfUnsubscribe, permission=PRIVILEGE_SUBSCRIBE)
        config.add_view(self.view_library_doc, context=ResourceLibraryDocRender, renderer='library_doc.jinja2', permission=PRIVILEGE_READ)
        config.add_view(self.view_library_asset, context=ResourceLibraryAsset, permission=PRIVILEGE_READ)
        config.add_view(self.view_refresh_library, context=ResourceLibraryRefresh, permission=PRIVILEGE_READ)
        config.add_view(self.view_refresh, context=ResourceRefresh)
        
        config.add_view(self.view_exception, context=Exception, renderer='exception.jinja2')
        config.add_view(self.exit, context=ResourceExit, renderer='json', permission=NO_PERMISSION_REQUIRED)

        config.add_view(self.view_exceptions_occurred_json, context=ResourceExceptionsJSON, renderer='json', permission=NO_PERMISSION_REQUIRED)
        config.add_view(self.view_exceptions_occurred, context=ResourceExceptionsFormatted, renderer='exceptions_formatted.jinja2', permission=NO_PERMISSION_REQUIRED)
        config.add_view(self.view_dummy, context=ResourceShelfInactive, renderer='shelf_inactive.jinja2')
        config.add_view(self.view_thing_delete, context=ResourceThingDelete)
        config.add_view(self.view_thing, context=ResourceThing)
        config.add_view(serve_robots, context=ResourceRobots, permission=NO_PERMISSION_REQUIRED)
        config.add_notfound_view(self.view_not_found, renderer='404.jinja2')
        config.scan()

        app = config.make_wsgi_app()
        return app
    
    @cr2e
    def view_thing(self, e):
        url = e.request.url
        if not url.endswith('/'):
            url += '/'
        url2 = url + 'views/syntax/'
        raise HTTPFound(url2)
    
    def _get_changes(self, e):
        changes = []
        for id_repo, repo in self.repos.items():   
            for change in repo.get_changes():
                
                change['repo_name'] = id_repo
                a = change['author']
                if a in e.session.app.user_db:
                    u = e.session.app.user_db[a]
                else:
                    logger.debug('Cannot find user %r' % a )
                    u = UserInfo(username=a, name=None, 
                                 password=None, email=None, website=None, affiliation=None, groups=[], subscriptions=[])
                change['user'] = u
                p = '/repos/{repo_name}/shelves/{shelf_name}/libraries/{library_name}/{spec_name}/views/syntax/'
                change['url'] = e.root + p.format(**change)

                #print('change: %s url = %s' % (change, change['url']))
                change['date_human'] =  datetime.datetime.fromtimestamp(change['date']).strftime('%b %d, %H:%M')
                changes.append(change)
                
        return changes
        
    @add_std_vars_context
    @cr2e
    def view_changes(self, e):
        return {
            'changes': self._get_changes(e),
        } 
    

    
    @add_std_vars_context
    @cr2e
    def view_thing_delete(self, e):
        name = e.thing_name
        basename = "%s.%s" % (name, e.spec.extension)
        logger.error('Deleting %s' % basename)
        filename = e.library.delete_file(basename)
        e.session.notify_deleted_file(e.shelf_name, e.library_name, filename)
        raise HTTPFound(e.request.referrer)
    
    
def serve_robots(request):  # @UnusedVariable
    body = "User-agent: *\nDisallow:"
    return Response(content_type='text/plain', body=body)

def get_url_library(e, shelf_name, library_name):
    url = e.root + '/repos/{repo_name}/shelves/{shelf_name}/libraries/{library_name}'
    url = url.format(shelf_name=shelf_name, repo_name=e.repo_name, library_name=library_name)
    return url

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

