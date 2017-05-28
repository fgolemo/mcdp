from contracts.utils import indent
from mcdp import MCDPConstants
from mcdp.logs import logger as logger_main
from mcdp.logs import logger_web_resource_tree as logger
import os

from pyramid.security import Allow, Authenticated, Everyone


Privileges = MCDPConstants.Privileges

class Resource(object):

    def __init__(self, name=None):
        if isinstance(name, unicode):
            name = name.encode('utf-8')
        self.name = name

    def get_subs(self):
        #print('iter not implemented for %s' % type(self).__name__)
        return None

    def getitem(self, key):  # @UnusedVariable
        subs = self.get_subs()
        if subs is None:
            return None
        return subs.get(key, None)

    def __iter__(self):
        subs = self.get_subs()
        if subs is not None:
            return sorted(subs).__iter__()
        return [].__iter__()

    def __repr__(self):
        if self.name is None:
            return '%s()' % type(self).__name__
        else:
            return '%s(%s)' % (type(self).__name__, self.name)

    def __getitem__(self, key):
        if isinstance(key, unicode):
            key = key.encode('utf8')
#         if key in ['login']:
#             return None
        r = self.getitem(key)
        if r is None:
            logger.debug('asked for %r - not found' % key)
            notfound = ResourceNotFoundGeneric(key)
            notfound.__parent__ = self
            return notfound

        if not hasattr(r, '__parent__'):
            r.__parent__ = self

        logger.debug('asked for %r - returning %r ' % (key, r))
        return r

    def show_ancestors(self):
        cs = get_all_contexts(self)
        s = '/'.join(str(_) for _ in cs)
        return s

    def get_request(self):
        ''' Looks up .request in the root '''
        cs = get_all_contexts(self)
        return cs[0].request

    def get_session(self):
        from mcdp_web.main import WebApp
        app = WebApp.singleton
        request = self.get_request()
        session = app.get_session(request)
        return session

class ResourceEndOfTheLine(Resource):
    ''' Always returns a copy of itself '''
    def __init__(self, name, orig_key_not_found=None, relative=None):
        '''
            name: name of last leaf
            orig_key_not_found: the first thing that was not found
            relative: tuple of names relative to orig_key_not_found
        '''
        if orig_key_not_found is None:
            orig_key_not_found = name
        self.relative = relative or ()
        self.orig_key_not_found = orig_key_not_found
        self.name = name
        
    def getitem(self, key):  # @UnusedVariable
        orig_key_not_found = self.orig_key_not_found
        relative = self.relative + (self.name,)
        return type(self)(name=key, relative=relative, orig_key_not_found=orig_key_not_found)
 
    def get_url_relative_to_not_found(self):
        return "/".join(self.relative[1:])
    
    def __repr__(self):
        url = self.get_url_relative_to_not_found()
        return '%s(%s, %s)' % (type(self).__name__, self.orig_key_not_found, url)

class ResourceNotFoundGeneric(ResourceEndOfTheLine):
    pass

def context_display_in_detail(context):
    ''' Returns a string that displays in detail the context tree and acls. '''
    s = ''
    cs = get_all_contexts(context)
    for c in cs:
        s += '%s' % c
        if hasattr(c, '__acl__'):
            s += '\n' + indent('\n'.join(str(_) for _ in c.__acl__), ' | ')
        s += '\n'
    return s


class MCDPResourceRoot(Resource):
    __acl__ = [
        (Allow, Authenticated, Privileges.VIEW_USER_LIST),
        (Allow, Authenticated, Privileges.VIEW_USER_PROFILE_PUBLIC),
    ]
    def __init__(self, request):  # @UnusedVariable
        self.name = 'root'
        self.request = request
        from mcdp_web.main import WebApp
        options = WebApp.singleton.options    # @UndefinedVariable
        
        if options.allow_anonymous:
            x = (Allow, Everyone, Privileges.ACCESS)
            if not x in MCDPResourceRoot.__acl__: 
                MCDPResourceRoot.__acl__.append(x)
            #logger.info('Allowing everyone to access')
        else:
            x = (Allow, Authenticated, Privileges.ACCESS)
            if not x in MCDPResourceRoot.__acl__: 
                MCDPResourceRoot.__acl__.append(x)
            #logger.info('Allowing authenticated to access')

    def get_subs(self):
        return {
            'tree': ResourceTree(),
            'repos': ResourceRepos(),
            'changes': ResourceChanges(),
            'exceptions': ResourceExceptionsJSON(),
            'exceptions_formatted': ResourceExceptionsFormatted(),
            'refresh': ResourceRefresh(),
            'exit': ResourceExit(),
            'login': ResourceLogin(),
            'logout': ResourceLogout(),
            'shelves': ResourceAllShelves(),
            'about': ResourceAbout(),
            'robots.txt': ResourceRobots(),
            'authomatic': ResourceAuthomatic(),
            'users': ResourceListUsers(),
            'confirm_bind': ResourceConfirmBind(),
            'confirm_bind_bind': ResourceConfirmBindBind(),
            'confirm_creation_similar': ResourceConfirmCreationSimilar(),
            'confirm_creation': ResourceConfirmCreation(),
            'confirm_creation_create': ResourceConfirmCreationCreate(),
            'db_view': ResourceDBView(),
            'search': ResourceSearchPage(),
        }

class ResourceConfirmBind(Resource): pass
class ResourceConfirmBindBind(Resource): pass
class ResourceConfirmCreationSimilar(Resource): pass
class ResourceConfirmCreation(Resource): pass
class ResourceConfirmCreationCreate(Resource): pass

class ResourceDBView(Resource):
    pass

class ResourceSearchPage(Resource):
    def get_subs(self):
        r = {}
        r[':query'] = ResourceSearchPageQuery()
        return r  

class ResourceSearchPageQuery(Resource): pass
        
         
class ResourceAbout(Resource): pass
class ResourceTree(Resource): pass

class ResourceListUsers(Resource):
    def getitem(self, key):
        return ResourceListUsersUser(key)

class ResourceListUsersUser(Resource):
    def __init__(self, name):
        Resource.__init__(self, name)
        self.__acl__ = [
            (Allow, name, Privileges.VIEW_USER_PROFILE_PRIVATE),
            (Allow, name, Privileges.EDIT_USER_PROFILE),
            (Allow, 'group:admin', Privileges.EDIT_USER_PROFILE),
            (Allow, 'group:admin', Privileges.VIEW_USER_PROFILE_PRIVATE),
            (Allow, 'group:admin', Privileges.VIEW_USER_PROFILE_INTERNAL),
            (Allow, 'group:admin', Privileges.IMPERSONATE_USER),
        ]

    def getitem(self, key):
        #print('key : %s' % key)
        if key == 'large.jpg':
            return ResourceUserPicture(self.name, 'large', 'jpg')
        if key == 'small.jpg':
            return ResourceUserPicture(self.name, 'small', 'jpg')
        if key == ':impersonate':
            return ResourceUserImpersonate(self.name)

class ResourceUserImpersonate(Resource):
    ''' Impersonate this user '''
    

    
class ResourceUserPicture(Resource):
    def __init__(self, name, size, data_format):
        self.name = name
        self.size = size
        self.data_format = data_format


class ResourceExit(Resource): pass
class ResourceLogin(Resource): pass
class ResourceLogout(Resource): pass
class ResourceChanges(Resource): pass
class ResourceAllShelves(Resource): pass

class ResourceShelves(Resource):

    def get_repo(self):
        session = self.get_session()
        repos = session.app.hi.db_view.repos
        repo_name = self.__parent__.name
        repo = repos[repo_name]
        return repo
    
    def getitem(self, key):
        session = self.get_session()
        ui = session.get_user_struct().info
        repo = self.get_repo()
        shelves = repo.shelves
        
        if not key in shelves:
            
            msg = 'Not found shelf %r in %s' % (key, sorted(shelves))
            logger_main.info(msg)
            return ResourceShelfNotFound(key)
        shelf = shelves[key]
        if not shelf.get_acl().allowed2(Privileges.READ, ui):
            return ResourceShelfForbidden(key)

        return ResourceShelf(key)

    def __iter__(self):
        session = self.get_session()
        ui = session.get_user_struct().info
        repo = self.get_repo()

        shelves = repo.shelves
        for id_shelf, shelf in shelves.items():
            if shelf.get_acl().allowed2(Privileges.READ, ui):
                yield id_shelf

class ResourceShelfForbidden(ResourceEndOfTheLine): pass
class ResourceShelfNotFound(ResourceEndOfTheLine): pass
class ResourceThingNotFound(ResourceEndOfTheLine): pass
class ResourceLibraryDocNotFound(ResourceEndOfTheLine): pass
class ResourceLibraryAssetNotFound(ResourceEndOfTheLine): pass

class ResourceShelvesShelfSubscribe(Resource): pass
class ResourceShelvesShelfUnsubscribe(Resource): pass
class ResourceExceptionsFormatted(Resource): pass
class ResourceExceptionsJSON(Resource): pass
class ResourceRefresh(Resource): pass

class ResourceLibrariesNew(Resource):
    
    def getitem(self, key):
        return ResourceLibrariesNewLibname(key)

class ResourceLibrariesNewLibname(Resource): pass

class ResourceLibraries(Resource):

    def getitem(self, key):
        subs = {
            ':new': ResourceLibrariesNew(),
        }
        if key in subs: return subs[key]

        libname = key
        shelf = context_get_shelf(self)
        if not libname in shelf.libraries:
            return ResourceLibraryNotFound(libname)
        return ResourceLibrary(libname)

    def __iter__(self):
        shelf = context_get_shelf(self)
        libraries = sorted(shelf.libraries)
        return libraries.__iter__()


class ResourceShelf(Resource):

    @property
    def __acl__(self):
        session = self.get_session()
        shelf = session.get_shelf(self.name)
        return shelf.get_acl().as_pyramid_acl()

    def __iter__(self):
        return ['libraries'].__iter__()

    def getitem(self, key):
        subs =  {
            ':subscribe': ResourceShelvesShelfSubscribe(self.name),
            ':unsubscribe': ResourceShelvesShelfUnsubscribe(self.name),
        }
        if key in subs: return subs[key]

        if key == 'libraries':
            session = self.get_session()
            if not self.name in session.shelves_used:
                msg = 'Cannot access libraries if not subscribed to shelf "%s".' % self.name
                msg += ' user: %s' % self.get_session().get_user_struct()
                logger.debug(msg)
                return ResourceShelfInactive(self.name)

            return ResourceLibraries()


class ResourceShelfInactive(ResourceEndOfTheLine):
    pass


class ResourceRepos(Resource):

    def getitem(self, key):
        session = self.get_session()
        repos = session.app.hi.db_view.repos
        if not key in repos:
            #msg = 'Could not find repository "%s".' % key
            return ResourceRepoNotFound(key)
        return ResourceRepo(key)

    def __iter__(self):
        session = self.get_session()
        repos = session.app.hi.db_view.repos
        return list(repos).__iter__()

class ResourceRepoNotFound(ResourceEndOfTheLine):
    pass

class ResourceRepo(Resource):
    def get_subs(self):
        return {'shelves':ResourceShelves()}

class ResourceLibraryNotFound(ResourceEndOfTheLine):
    pass

class ResourceLibrary(Resource):

    def __iter__(self):
        from mcdp_library.specs_def import specs
        options = list(specs)
        options.append('interactive')
        return options.__iter__()

    def getitem(self, key):
        if key == 'refresh_library':
            return ResourceLibraryRefresh()
        if key == 'interactive':
            return ResourceLibraryInteractive()

        library = context_get_library(self)

        if key.endswith('.html'):
            docname = os.path.splitext(key)[0]
#             filename = '%s.%s' % (docname, MCDPConstants.ext_doc_md)
            if not docname in library.documents:
                return ResourceLibraryDocNotFound(docname)

            return ResourceLibraryDocRender(docname)

        if '.' in key:
            if not library.file_exists(key):
                return ResourceLibraryAssetNotFound(key)
            return ResourceLibraryAsset(key)
        return ResourceThings(key)

class ResourceLibraryDocRender(Resource): pass
class ResourceLibraryAsset(Resource): pass

class ResourceLibraryInteractive(Resource):
    def getitem(self, key):
        if key == 'mcdp_value':
            return ResourceLibraryInteractiveValue()

class ResourceLibraryInteractiveValue(Resource):
    def getitem(self, key):
        if key == 'parse':
            return ResourceLibraryInteractiveValueParse()


class ResourceLibraryInteractiveValueParse(Resource): pass

class ResourceLibraryRefresh(Resource): pass

class ResourceThings(Resource):
    
    def __init__(self, specname):
        Resource.__init__(self, specname)
        self.specname = self.name

    def __iter__(self):
        things = context_get_things(self)
        for x in things:
            yield x

    def getitem(self, key):
        if key == 'new': return ResourceThingsNewBase()
        
        things = context_get_things(self)
        if not key in things:
            try:
                from mcdp_hdb_mcdp.library_view import get_soft_match
                key2 = get_soft_match(key, list(things))
            except KeyError:
                return ResourceThingNotFound(key)
            else:
                if MCDPConstants.allow_soft_matching:
                    return ResourceThing(key2)
                else:
                    msg = 'Soft matching %s -> %s' % (key, key2)
                    raise Exception(msg)
        else:
            return ResourceThing(key)

    def __repr__(self):
        return '%s(specname=%s)' % (type(self).__name__, self.specname)


class ResourceThingsNewBase(Resource):
    def getitem(self, key):
        return ResourceThingsNew(key)

class ResourceThingsNew(Resource): pass

class ResourceThing(Resource):

    def __iter__(self):
        return ['views'].__iter__()

    def getitem(self, key):
        subs =  {
            'views': ResourceThingViews(),
            ':delete': ResourceThingDelete(),
            ':rename': ResourceThingRename(),
        }
        return subs.get(key, None)

class ResourceThingDelete(Resource):
    pass

class ResourceThingRename(Resource):
    pass

class ResourceThingViews(Resource):

    def __iter__(self):
        options = ['syntax', 'edit_fancy']
        if self.__parent__.__parent__.specname == 'models':
            options.extend(['dp_graph', 'dp_tree', 'ndp_graph', 'ndp_repr', 'solver2', 'images', 'solver'])
        return options.__iter__()

    def getitem(self, key):
        subs =  {
            'syntax': ResourceThingViewSyntax(),
            'edit_fancy': ResourceThingViewEditor(),
        }
        if self.__parent__.__parent__.specname == 'models':
            subs2 = {
                'dp_graph': ResourceThingViewDPGraph(),
                'dp_tree': ResourceThingViewDPTree(),
                'ndp_graph': ResourceThingViewNDPGraph(),
                'ndp_repr': ResourceThingViewNDPRepr(),
                'solver2': ResourceThingViewSolver(),
                'images': ResourceThingViewImages(),
                'solver': ResourceThingViewSolver0(),
            }
            subs.update(**subs2)

        return subs.get(key, None)

class ResourceThingViewImages(Resource):
    def getitem(self, key):
        which, data_format = key.split('.')
        return ResourceThingViewImagesOne(which.encode('utf8'), data_format.encode('utf8'))

class ResourceThingView(Resource): pass
class ResourceThingViewSyntax(ResourceThingView): pass
class ResourceThingViewDPGraph(ResourceThingView): pass
class ResourceThingViewDPTree(ResourceThingView): pass
class ResourceThingViewNDPGraph(ResourceThingView): pass
class ResourceThingViewNDPRepr(ResourceThingView): pass
class ResourceThingViewSolver(ResourceThingView):
    def getitem(self, key):
        subs =  {
            'submit': ResourceThingViewSolver_submit(),
            'display.png': ResourceThingViewSolver_display_png(),
            'display1u': ResourceThingViewSolver_display1u(),
            'display1u.png': ResourceThingViewSolver_display1u_png(),
        }
        return subs.get(key, None)

class ResourceThingViewSolver_submit(Resource): pass
class ResourceThingViewSolver_display_png(Resource): pass
class ResourceThingViewSolver_display1u(Resource): pass
class ResourceThingViewSolver_display1u_png(Resource): pass

class ResourceThingViewSolver0(ResourceThingView):
    def getitem(self, key):
        return ResourceThingViewSolver0Axis( key)

class ResourceThingViewSolver0Axis(ResourceThingView):
    def getitem(self, key):
        return ResourceThingViewSolver0AxisAxis(self.name, key)

class ResourceThingViewSolver0AxisAxis(ResourceThingView):
    def __init__(self, fun_axes, res_axes):
        self.fun_axes = fun_axes
        self.res_axes = res_axes
        self.name = '%s-%s' % (fun_axes, res_axes)
    def getitem(self, key):
        subs = {
            'addpoint': ResourceThingViewSolver0AxisAxis_addpoint(),
            'getdatasets': ResourceThingViewSolver0AxisAxis_getdatasets(),
            'reset': ResourceThingViewSolver0AxisAxis_reset(),
        }
        return subs.get(key, None)

class ResourceThingViewSolver0AxisAxis_addpoint(Resource): pass
class ResourceThingViewSolver0AxisAxis_getdatasets(Resource): pass
class ResourceThingViewSolver0AxisAxis_reset(Resource): pass

class ResourceThingViewEditor(ResourceThingView):
    def getitem(self, key):
        subs =  {
            'ajax_parse': ResourceThingViewEditorParse(),
            'save': ResourceThingViewEditorSave(),
        }
        if key in subs:
            return subs[key]

        if key.startswith('graph.'):
            _, text_hash, data_format = key.split('.')
            return ResourceThingViewEditorGraph(text_hash.encode('utf8'), data_format.encode('utf8'))


class ResourceThingViewEditorParse(Resource): pass
class ResourceThingViewEditorSave(Resource): pass

class ResourceThingViewEditorGraph(Resource):
    def __init__(self, text_hash, data_format):
        self.text_hash = text_hash
        self.data_format = data_format
        self.name = 'graph.%s.%s' % (text_hash, data_format)

class ResourceThingViewImagesOne(Resource):
    def __init__(self, which, data_format):
        self.which = which
        self.data_format = data_format
        self.name = '%s.%s' % (which, data_format)

class ResourceRobots(Resource): pass
class ResourceAuthomatic(Resource):
    def get_subs(self):
        session = self.get_session()
        config = session.app.get_authomatic_config()
        subs =  {
            'github': ResourceAuthomaticProvider('github'),
            'facebook': ResourceAuthomaticProvider('facebook'),
            'google': ResourceAuthomaticProvider('google'),
            'linkedin': ResourceAuthomaticProvider('linkedin'),
            'amazon': ResourceAuthomaticProvider('amazon'),
        }
        for k in list(subs):
            if not k in config:
                del subs[k]
            
        return subs

class ResourceAuthomaticProvider(Resource): pass

def get_all_contexts(context):
    if hasattr(context, '__parent__'):
        return get_all_contexts(context.__parent__) + (context,)
    else:
        return (context,)

def get_from_context(rclass, context):
    a = get_all_contexts(context)
    for _ in a:
        if isinstance(_, rclass):
            return _
    return None

def is_in_context(rclass, context):
    return get_from_context(rclass, context) is not None

def context_get_shelf_name(context):
    return get_from_context(ResourceShelf, context).name

def context_get_repo_name(context):
    return get_from_context(ResourceRepo, context).name

def context_get_repo(context):
    session = context.get_session()
    repo_name = context_get_repo_name(context)
    repos = session.app.hi.db_view.repos
    repo = repos[repo_name]
    return repo

def context_get_shelf(context):
    repo = context_get_repo(context)
    shelf_name = context_get_shelf_name(context)
    shelf = repo.shelves[shelf_name]
    return shelf

def context_get_library(context):
    library_name = context_get_library_name(context)
    shelf = context_get_shelf(context)
    library = shelf.libraries[library_name]
    return library

def context_get_things(context):
    library = context_get_library(context)
    specname = get_from_context(ResourceThings, context).specname
    things  = library.things.child(specname)
    return things

def context_get_library_name(context):
    library_name = get_from_context(ResourceLibrary, context).name
    return library_name

def context_get_spec(context):
    from mcdp_web.editor_fancy.app_editor_fancy_generic import specs
    specname = get_from_context(ResourceThings, context).specname
    spec = specs[specname]
    return spec
