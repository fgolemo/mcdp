# -*- coding: utf-8 -*-
from collections import OrderedDict
import datetime
import os
import sys
import time
import traceback
import urlparse
from wsgiref.simple_server import make_server

from authomatic.adapters import WebObAdapter
from authomatic import Authomatic
from contracts.utils import indent, check_isinstance
import git.cmd  # @UnusedImport
from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.config import Configurator
from pyramid.httpexceptions import HTTPFound
from pyramid.renderers import JSONP, render_to_response
from pyramid.response import Response
from pyramid.security import NO_PERMISSION_REQUIRED, remember
from pyramid.session import SignedCookieSessionFactory
from quickapp import QuickAppBase

from mcdp import MCDPConstants
from mcdp import logger
from mcdp.exceptions import DPSemanticError, DPSyntaxError
from mcdp_docs import render_complete
from mcdp_library import MCDPLibrary
from mcdp_repo import MCDPGitRepo, MCDPythonRepo
from mcdp_shelf import PRIVILEGE_ACCESS, PRIVILEGE_READ, PRIVILEGE_SUBSCRIBE, PRIVILEGE_DISCOVER, PRIVILEGE_WRITE
from mcdp_user_db import UserDB, UserInfo
from mcdp_utils_misc import create_tmpdir, duration_compact, dir_from_package_name
from mcdp_utils_misc import format_list
from mcdp_utils_misc.memoize_simple_imp import memoize_simple
from mcdp_web.resource_tree import ResourceAuthomaticProvider
from mcdp_web.utils0 import add_std_vars_context_no_redir

from .confi import describe_mcdpweb_params, parse_mcdpweb_params_from_dict
from .editor_fancy import AppEditorFancyGeneric
from .environment import cr2e
from .images.images import WebAppImages, get_mime_for_format
from .interactive.app_interactive import AppInteractive
from .qr.app_qr import AppQR
from .resource_tree import MCDPResourceRoot, ResourceLibraries, ResourceLibrary,  ResourceLibraryRefresh, ResourceRefresh, ResourceExit, ResourceLibraryDocRender, ResourceLibraryAsset, ResourceRobots, ResourceShelves, ResourceShelvesShelfUnsubscribe, ResourceShelvesShelfSubscribe, ResourceExceptionsFormatted, ResourceExceptionsJSON, ResourceShelf, ResourceLibrariesNewLibname, Resource, context_display_in_detail, ResourceShelfInactive, ResourceThingDelete, ResourceChanges, ResourceTree, ResourceThing, ResourceRepos, ResourceRepo, ResourceThings, ResourceLibraryInteractive
from .resource_tree import ResourceAllShelves, ResourceShelfForbidden,\
    ResourceShelfNotFound, ResourceRepoNotFound, ResourceLibraryAssetNotFound,\
    ResourceLibraryDocNotFound, ResourceNotFoundGeneric, ResourceAbout
from .security import AppLogin, groupfinder
from .sessions import Session
from .solver.app_solver import AppSolver
from .solver2.app_solver2 import AppSolver2
from .status import AppStatus
from .utils.image_error_catch_imp import response_image
from .utils.response import response_data
from .utils0 import add_other_fields, add_std_vars_context
from .visualization.app_visualization import AppVisualization
import urllib2


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
    
    def __init__(self, options, settings):
        from mcdp_library_tests.create_mockups import write_hierarchy
        self.options = options
        self.settings =settings
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
            db = {
                'anonymous.mcdp_user': {
                    'user.yaml' : '''
                        name: Anonimo
                    '''
                }
            }
            if not os.path.exists(self.options.users):
                os.makedirs(self.options.users)
#             repo = Repo.init(self.options.users)
#             
#             origin = repo.create_remote('origin', url='file://invalid')
#             for filename in create_file_and_yield(db, self.options.users):
# #             print('written %r' % filename)
# #             print('untracked_files: %s' % repo0.untracked_files)
# #             print('Dirty: %s' % repo0.is_dirty(untracked_files=True))
#                 repo.index.add(repo.untracked_files)
#                 message = 'author: system'
#                 author = Actor('system', 'system')
#                 repo.index.commit(message, author=author)
                
            write_hierarchy(self.options.users, db)
            

        self.repos = {}
        REPO_BUNDLED = 'bundled'
        REPO_USERS = 'global'
        if self.options.load_mcdp_data:
            desc_short = 'Contains models bundled with the code.'
            if os.path.exists('.git'):
                logger.info('Loading mcdp_data repo as MCDPGitRepo')
                b = MCDPGitRepo(where='.', desc_short=desc_short)
            else:
                logger.info('Loading mcdp_data repo as MCDPythonRepo')
                b = MCDPythonRepo('mcdp_data', desc_short=desc_short)
                    
            self.repos[REPO_BUNDLED]  = b
        else:
            logger.info('Not loading mcdp_data')
            
        if self.options.users is not None:
            self.user_db = UserDB(self.options.users)            
            desc_short = 'Global database of shared models.'
            is_git = os.path.exists(os.path.join(self.options.users, '.git'))
            if is_git:
                self.repos[REPO_USERS] = MCDPGitRepo(where=self.options.users, desc_short=desc_short)

        shelf2repo = {}
        for id_repo, repo in self.repos.items():
            shelves = repo.get_shelves()
            
            logger.info('repo %s: %s' % (id_repo, sorted(shelves)))
            
            for shelf_name in shelves:
                if shelf_name in shelf2repo:
                    msg = 'Shelf %r in %r and %r' % (shelf_name, id_repo, shelf2repo[shelf_name])
                    raise ValueError(msg)
                shelf2repo[shelf_name] = id_repo

            self.all_shelves.update(shelves)
        
        picture = 'http://graph.facebook.com/10154724108563171/picture?type=large'
        h = urllib2.urlopen(picture)
        logger.info('urlp opened  %s' % h)
        jpg = h.read()
        logger.info('read %s bytes' % len(jpg)) 
        
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
    
    @add_std_vars_context_no_redir
    @cr2e
    def view_resource_not_found(self, e):  
        e.request.response.status = 404
        return {}
    
    @add_std_vars_context_no_redir
    @cr2e
    def view_resource_forbidden(self, e): 
        e.request.response.status = 403
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
            
            res = {
                'error': error,
                'library_name': new_library_name,
                'url_edit': url_edit,
            }
            add_other_fields(self, res, e.request, context=e.context)
            template = 'error_library_exists.jinja2'
            e.request.response.status = 409  # Conflict
            return render_to_response(template, res, request=e.request, 
                                      response=e.request.response)
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

    def refresh_library(self, e):
        # nuclear option
        e.session.refresh_libraries()

    @cr2e
    def view_refresh_library(self, e):  # @UnusedVariable
        """ Refreshes the current library (if external files have changed) 
            then reloads the current url. """
#         self._refresh_library(request) 
        # Note this currently is equivalent to global refresh
        return self.view_refresh(e.context, e.request);

    @cr2e
    def view_refresh(self, e): 
        """ Refreshes all """
        self.refresh_library(e) 
        if e.request.referrer is None:
            redirect = self.get_root_relative_to_here(e.request)
            logger.info('REFRESH')
            logger.info('context.url = %s' % e.request.url)
            logger.info('redirect = %s' % redirect)
        else:
            redirect = e.request.referrer
        raise HTTPFound(redirect)

    @cr2e
    def view_not_found(self, e):
        e.request.response.status = 404
        url = e.request.url
        referrer = e.request.referrer
        #print('context: %s' % e.context)
        self.exceptions.append('Path not found.\n url: %s\n referrer: %s' % (url, referrer))
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
            
        compact = (DPSemanticError, DPSyntaxError)
        if isinstance(exc, compact):
            s = exc.__str__()
        else:
            s = traceback.format_exc(exc)

        self.note_exception(exc, request=request)
 
        u = unicode(s, 'utf-8')
        logger.error(u.encode('utf8'))
        root = self.get_root_relative_to_here(request)
        res = {
            'exception': u,
            # 'url_refresh': url_refresh,
            'root': root,
            'static': root + '/static'
        }  
        return res
 
    def note_exception(self, exc, request=None, context=None):
        check_isinstance(exc, BaseException)
        n = ''
        if request is not None:   
            url = request.url
            referrer = request.referrer
            n += 'Error during serving this URL:'
            n += '\n url: %s' % url
            n += '\n referrer: %s' % referrer

        if context is not None:
            n += '\n\n' + context_display_in_detail(context) + '\n'
            
        ss = traceback.format_exc(exc)
        n += '\n' + indent(ss, '| ')
        self.exceptions.append(n)
    
    def png_error_catch2(self, request, func):
        """ func is supposed to return an image response.
            If it raises an exception, we create
            an image with the error and then we add the exception
            to the list of exceptions.
            
             """
        try:
            return func()
        except Exception as e:
            s = traceback.format_exc(e)

            try:
                logger.error(s)
            except UnicodeEncodeError:
                pass

            self.note_exception(e, request=request)            
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
            raise ValueError()
        
        parsed = urlparse.urlparse(request.url) 
        path = parsed.path
        
        if not path.endswith('/'):
            last = path.rfind('/')
            path = path[:last]

        if path == '':
            return '/'
        r = os.path.relpath('/', path)
        return r

    @add_std_vars_context_no_redir
    @cr2e
    def view_library_asset_not_found(self, e):
        e.request.response.status = 404
        return {}

    @add_std_vars_context_no_redir
    @cr2e
    def view_library_doc_not_found(self, e):
        e.request.response.status = 404
        return {}
    
    @add_std_vars_context_no_redir
    @cr2e
    def view_library_doc(self, e):
        """ '/libraries/{library}/{document}.html' """
        # f['data'] not utf-8
        # reopen as utf-8
        document = e.context.name
#         filename = '%s.%s' % (document, MCDPConstants.ext_doc_md)
#         if not e.library.file_exists(filename):
#             res = {}
#             add_other_fields(self, res, e.request, context=e.context)
#             response = e.request.response
#             response.status = 404 # not found
#             template = 'library_doc_not_found.jinja2'
#             return render_to_response(template, res, request=e.request, response=response)

        try:
            html = self._render_library_doc(e, document)
        except DPSyntaxError as exc:
            res = {}
            res['error'] = exc
            res['title'] = document
            return res 
        # we work with utf-8 strings
        assert isinstance(html, str)
        # but we need to convert to unicode later
        html = unicode(html, 'utf-8')
        res = {}
        res['contents'] = html
        res['title'] = document
        res['print'] = bool(e.request.params.get('print', False))
        return res

    def _render_library_doc(self, e, document):
        strict = int(e.request.params.get('strict', '0'))
        filename = '%s.%s' % (document, MCDPConstants.ext_doc_md)
            
        f = e.library._get_file_data(filename)
        
        realpath = f['realpath']
        # read unicode
        import codecs 
        data_unicode = codecs.open(realpath, encoding='utf-8').read()
        data_str = data_unicode.encode('utf-8')
        raise_errors = bool(strict)
        html = render_complete(library=e.library, s=data_str, 
                               realpath=realpath, raise_errors=raise_errors)
        return html

    @cr2e
    def view_library_asset(self, e):
        name = e.context.name
        asset = os.path.splitext(name)[0]
        ext = os.path.splitext(name)[1][1:]
        filename = '%s.%s' % (asset, ext)
        try:
            f = e.library._get_file_data(filename)
        except DPSemanticError as exc:
            res = {
                'error': exc, 
            }
            add_other_fields(self, res, e.request, context=e.context)
            response = e.request.response
            response.status = 404 # not found
            template = 'asset_not_found.jinja2'
            return render_to_response(template, res, request=e.request, response=response)
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
        root_factory =MCDPResourceRoot
        config = Configurator(root_factory=root_factory, settings=self.settings)
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

        config.add_view(self.view_dummy, context=ResourceAbout, renderer='about.jinja2')
        config.add_view(self.view_index, context=MCDPResourceRoot, renderer='index.jinja2')
        config.add_view(self.view_dummy, context=ResourceLibraries, renderer='list_libraries.jinja2')
        config.add_view(self.view_dummy, context=ResourceRepos, renderer='repos.jinja2')
        config.add_view(self.view_dummy, context=ResourceLibraryInteractive, renderer='empty.jinja2')
        
        config.add_view(self.view_dummy, context=ResourceLibrary, renderer='library_index.jinja2', permission=PRIVILEGE_READ)
        config.add_view(self.view_dummy, context=ResourceThings, renderer='library_index.jinja2', permission=PRIVILEGE_READ)  # same as above
    
        config.add_view(self.view_dummy, context=ResourceRepo, renderer='shelves_index.jinja2')
        config.add_view(self.view_dummy, context=ResourceShelves, renderer='shelves_index.jinja2') # same as above
        config.add_view(self.view_dummy, context=ResourceAllShelves, renderer='shelves_index.jinja2') # same as above
        config.add_view(self.view_changes, context=ResourceChanges, renderer='changes.jinja2')
        config.add_view(self.view_tree, context=ResourceTree, renderer='tree.jinja2')
        config.add_view(self.view_not_found_generic, context=ResourceNotFoundGeneric, renderer='not_found_generic.jinja2', permission=NO_PERMISSION_REQUIRED)
        config.add_view(self.view_shelf_library_new, context=ResourceLibrariesNewLibname, permission=PRIVILEGE_WRITE)
        config.add_view(self.view_shelf, context=ResourceShelf, renderer='shelf.jinja2', permission=PRIVILEGE_DISCOVER)
        config.add_view(self.view_shelves_subscribe, context=ResourceShelvesShelfSubscribe, permission=PRIVILEGE_SUBSCRIBE)
        config.add_view(self.view_shelves_unsubscribe, context=ResourceShelvesShelfUnsubscribe, permission=PRIVILEGE_SUBSCRIBE)
        config.add_view(self.view_library_doc, context=ResourceLibraryDocRender, renderer='library_doc.jinja2', permission=PRIVILEGE_READ)
        config.add_view(self.view_library_doc_not_found, context=ResourceLibraryDocNotFound, renderer='library_doc_not_found.jinja2', permission=PRIVILEGE_READ)
        config.add_view(self.view_library_asset_not_found, context=ResourceLibraryAssetNotFound, renderer='asset_not_found.jinja2', permission=PRIVILEGE_READ)
        config.add_view(self.view_library_asset, context=ResourceLibraryAsset, permission=PRIVILEGE_READ)
        config.add_view(self.view_refresh_library, context=ResourceLibraryRefresh, permission=PRIVILEGE_READ)
        config.add_view(self.view_refresh, context=ResourceRefresh)
        
        config.add_view(self.view_exception, context=Exception, renderer='exception.jinja2')
        config.add_view(self.exit, context=ResourceExit, renderer='json', permission=NO_PERMISSION_REQUIRED)

        config.add_view(self.view_exceptions_occurred_json, context=ResourceExceptionsJSON, renderer='json', permission=NO_PERMISSION_REQUIRED)
        config.add_view(self.view_exceptions_occurred, context=ResourceExceptionsFormatted, renderer='exceptions_formatted.jinja2', permission=NO_PERMISSION_REQUIRED)
        
        config.add_view(self.view_dummy, context=ResourceShelfNotFound, renderer='shelf_not_found.jinja2')
        config.add_view(self.view_dummy, context=ResourceShelfForbidden, renderer='shelf_forbidden.jinja2')
        config.add_view(self.view_dummy, context=ResourceShelfInactive, renderer='shelf_inactive.jinja2')
        config.add_view(self.view_resource_not_found, context=ResourceRepoNotFound, renderer='repo_not_found.jinja2')
        config.add_view(self.view_thing_delete, context=ResourceThingDelete)
        config.add_view(self.view_thing, context=ResourceThing)
        config.add_view(serve_robots, context=ResourceRobots, permission=NO_PERMISSION_REQUIRED)
        config.add_notfound_view(self.view_not_found, renderer='404.jinja2')
        config.scan()
    
        config.add_view(self.view_authomatic, context=ResourceAuthomaticProvider)
        self.get_authomatic_config()
        app = config.make_wsgi_app()
        return app
    
    @memoize_simple
    def get_authomatic_config(self):
        CONFIG = {}
        from authomatic.providers import oauth2
        if 'google.consumer_key' in self.settings:
            google_consumer_key = self.settings['google.consumer_key'] 
            google_consumer_secret = self.settings['google.consumer_secret']
            CONFIG['google'] = {                   
                    'class_': oauth2.Google,
                    'consumer_key':  google_consumer_key,
                    'consumer_secret': google_consumer_secret,
                    'scope': ['profile', 'email'],
            }
            logger.info('Configured Google authentication.')
        else:
            logger.warn('No Google authentication configuration found.')
        
        if 'facebook.consumer_key' in self.settings:
            oauth2.Facebook.user_info_url = 'https://graph.facebook.com/v2.5/me?fields=id,first_name,last_name,picture,email,gender,timezone,location,middle_name,name_format,third_party_id,website,birthday,locale'
            facebook_consumer_key = self.settings['facebook.consumer_key'] 
            facebook_consumer_secret = self.settings['facebook.consumer_secret']
            CONFIG['facebook'] = {                   
                    'class_': oauth2.Facebook,
                    'consumer_key':  facebook_consumer_key,
                    'consumer_secret': facebook_consumer_secret,
                    'scope': ['public_profile', 'email'],
            }
            logger.info('Configured Facebook authentication.')
        else:
            logger.warn('No Facebook authentication configuration found.')
            
        if 'github.consumer_key' in self.settings:
            github_consumer_key = self.settings['github.consumer_key'] 
            github_consumer_secret = self.settings['github.consumer_secret']
            CONFIG['github'] =  {
                'class_': oauth2.GitHub,
                'consumer_key': github_consumer_key,
                'consumer_secret': github_consumer_secret,
                'access_headers': {'User-Agent': 'PyMCDP'},
            }
            logger.info('Configured Github authentication.')
        else:
            logger.warn('No Github authentication configuration found.')
        return CONFIG
    
    @cr2e
    def view_authomatic(self, e):
        response = Response()
        p = urlparse.urlparse(e.request.url)
        logger.info(p)
        if '127.0.0.1' in p.netloc:
            msg = 'The address 127.0.0.1 cannot be used with authentication.'
            raise ValueError(msg)
        provider_name = e.context.name
        logger.info('using provider %r' % provider_name)
        
        config = self.get_authomatic_config()
        authomatic = Authomatic(config=config, secret='some random secret string')
        result = authomatic.login(WebObAdapter(e.request, response), provider_name)
        
        if not result:
            return response
        
        # If there is result, the login procedure is over and we can write to response.
        response.write('<a href="..">Home</a>')
        
        if result.error:
            # Login procedure finished with an error.
            response.status = 500
            response.write(u'<h2>Damn that error: {0}</h2>'.format(result.error.message))
            return response
        elif result.user:
            # OAuth 2.0 and OAuth 1.0a provide only limited user data on login,
            # We need to update the user to get more info.
            #if not (result.user.name and result.user.id):
            result.user.update()
            
            
            s = "user info: \n"
            for k, v in result.user.__dict__.items():
                s += '\n %s  : %s' % (k,v)
            print(s)
            
            next_location = e.root
            self.handle_auth_success(e, provider_name, result, next_location)

            response.write('<pre>'+s+'</pre>')
            # Welcome the user.
            response.write(u'<h1>Hi {0}</h1>'.format(result.user.name))
            response.write(u'<h2>Your id is: {0}</h2>'.format(result.user.id))
            response.write(u'<h2>Your email is: {0}</h2>'.format(result.user.email))
        
        # just regular login
        return response
        
    def handle_auth_success(self, e, provider_name, result, next_location):
        assert result.user
        # 1) If we are currently logged in:
        #    a) if we match to current account, do nothing.
        #    b) if we match with another account, log with that account
        #    c) if we don't match, ask the user if they want to bound
        #        this account to the MCDP account
        # 2) If we are not currently logged in:
        #    a) if we can match the Openid with an existing account, because:
        #         i. same email  or
        #        ii. same name (ignore conflict for now)
        #       then we log in
        #    b) if not, we ask the user if they want to create an account.
        
        # get the data
        name = result.user.name
        email = result.user.email
        picture = result.user.picture

        if provider_name == 'github':
            username = result.user.username 
            website = result.user.data['blog']
            affiliation = result.user.data['company']
        elif provider_name == 'facebook':
            if name is None:
                msg = 'Could not get name from Facebook so cannot create username.'
                raise Exception(msg)

            username = name.replace(' ','_').lower() 
            website = None
            affiliation = None
        elif provider_name == 'google':
            if name is None:
                msg = 'Could not get name from Google so cannot create username.'
                raise Exception(msg)
            username = name.replace(' ','_').lower()
            website = result.user.link
            website = None
            affiliation = None
#             * first_name
#             * gender
#             * id
#             * last_name
#             
        else:
            assert False, provider_name
        best = self.user_db.best_match(username, name, email)
        res = {}
        currently_logged_in = e.username is not None
        if currently_logged_in:
            if best is not None:
                if best.username ==  e.username:
                    # do nothing
                    res['message'] = 'Already authenticated'
                    raise HTTPFound(location=next_location)
                else:
                    logger.info('Switching user to %r.' % best.username)
                    self.success_auth(e.request, best.username, next_location)
            else:
                # no match
                res['message'] = 'Do you want to bind account to this one?'
                confirm_bind = e.root + '/confirm_bind?user=xxx'
                raise HTTPFound(location=confirm_bind)
        else:
            # not logged in
            if best is not None:
                # user already exists: login 
                self.success_auth(e.request, best.username, next_location)
            else:
                # not logged in, and the user does not exist already
                # we create an accounts
                res = {}
                res['username']= username
                res['name'] = name
                res['password'] = None
                res['email'] = email
                res['website'] = website
                res['affiliation'] = affiliation
                logger.info('Reading picture %s' % picture)
                try:
                    h = urllib2.urlopen(picture)
                    logger.info('urlp opened  %s' % h)
                    jpg = h.read()
                    logger.info('read %s bytes' % len(jpg)) 
                    res['picture'] = jpg
                except BaseException as e:
                    logger.error(e)
                    res['picture'] = None
                for k in res:
                    if isinstance(res[k], unicode):
                        res[k] = res[k].encode('utf8')
                res['subscriptions'] = []
                res['groups'] = ['account_created_automatically',
                                 'account_created_using_%s' % provider_name]
                u = UserInfo(**res) 
                self.user_db.users[username] = u
                self.user_db.save_user(username, new_user=True)
                self.success_auth(e.request, username, next_location)
    
    def success_auth(self, request, username, next_location):
        if not username in self.user_db:
            msg = 'Could not find user %r' % username
            raise Exception(msg)
        logger.info('successfully authenticated user %s' % username)
        headers = remember(request, username)
        raise HTTPFound(location=next_location, headers=headers)
    
    @cr2e
    def view_thing(self, e):
        url = e.request.url
        if not url.endswith('/'):
            url += '/'
        url2 = url + 'views/syntax/'
        logger.debug('Redirect to  ' + url2)
        raise HTTPFound(url2)
    
    def _get_changes(self, e):
        def shelf_privilege(repo_name, sname, privilege):
            repo = e.session.repos[repo_name]
            if not sname in repo.shelves:
                msg = 'Cannot find shelf "%s" in repo "%s".' % (sname, repo_name)
                msg += '\n available: ' + format_list(repo.shelves)
                raise ValueError(msg)
            acl = repo.shelves[sname].get_acl()
            return acl.allowed2(privilege, e.user)
        
        def shelf_subscribed(repo_name, shelf_name):
            return shelf_name in e.user.subscriptions # XXX

        changes = []
        for id_repo, repo in self.repos.items():   
            for change in repo.get_changes():
                
                if not shelf_privilege(id_repo, change['shelf_name'], PRIVILEGE_READ):
                    continue
                
                change['repo_name'] = id_repo
                a = change['author']
                if a in e.session.app.user_db:
                    u = e.session.app.user_db[a]
                else:
                    #logger.debug('Cannot find user %r' % a )
                    u = UserInfo(username=a, name=None, 
                                 password=None, email=None, website=None, affiliation=None, groups=[], subscriptions=[],
                                 picture=None)
                change['user'] = u
                p = '{root}/repos/{repo_name}/shelves/{shelf_name}/libraries/{library_name}/{spec_name}/{thing_name}/views/syntax/'
                
                subscribed = shelf_subscribed(id_repo, change['shelf_name'])
                
                if change['exists'] and subscribed:
                    change['url'] = p.format(root=e.root, **change)
                else:
                    change['url'] = None
 
                
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
    def view_not_found_generic(self, e):
        e.request.response.status = 404
        res = {
            'context_detail': context_display_in_detail(e.context)
        }
        return res

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
    url = '{root}/repos/{repo_name}/shelves/{shelf_name}/libraries/{library_name}'
    url = url.format(root=e.root, shelf_name=shelf_name, repo_name=e.repo_name, library_name=library_name)
    return url

class MCDPWeb(QuickAppBase):
    """ Runs the MCDP web interface. """

    def define_program_options(self, params):
        describe_mcdpweb_params(params)
        params.add_int('port', default=8080, help='Port to listen to.')
        
    def go(self):
        options = self.get_options()
        settings = {        
        }

        wa = WebApp(options, settings=settings)
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
            
def app_factory(global_config, **settings0):  # @UnusedVariable
    settings = get_only_prefixed(settings0, 'mcdp_web.')
    #print('app_factory settings %s' % settings)
    options = parse_mcdpweb_params_from_dict(settings)
    
    wa = WebApp(options, settings=settings0)
    app = wa.get_app()
    return app

mcdp_web_main = MCDPWeb.get_sys_main()

