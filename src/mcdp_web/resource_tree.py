from pyramid.security import Allow, Authenticated, Everyone
import os

'''

root
    login
    logout
    libraries
        <libname> [read]
            refresh_library
            interactive
                mcdp_value
            <specname>
                new/<thingname>
                <thingname>
                    <views>
                        solver
                        edit_fancy [write]
                            ajax_parse
                            save
    shelves
    exceptions
    exceptions_formatted
    refresh
    exit
'''

from mcdp_shelf.access import PRIVILEGE_ACCESS
from contracts.utils import indent

class Resource(object):
    
    def __init__(self, name=None):
        if isinstance(name,unicode):
            name = name.encode('utf-8')
        self.name = name
        
    def getitem(self, key):  # @UnusedVariable
        return None
    
    def __repr__(self):
        if self.name is None:
            return '%s()' % type(self).__name__
        else:
            return '%s(%s)' % (type(self).__name__, self.name)
    
    def __getitem__(self, key):
        r = self.getitem(key)
        if r is None:
            print('asked for %r - not found' % key)
            raise KeyError(key)
        
        if not hasattr(r, '__parent__'):
            r.__parent__ = self
        
        print('asked for %r - returning %r ' % (key, r))
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

    def __init__(self, request):  # @UnusedVariable
        self.name = 'root'
        self.request = request
        from mcdp_web.main import WebApp
        options = WebApp.singleton.options    # @UndefinedVariable
        self.__acl__ = []
        if options.allow_anonymous:
            self.__acl__.append((Allow, Everyone, PRIVILEGE_ACCESS))
            #logger.info('Allowing everyone to access')
        else:
            self.__acl__.append((Allow, Authenticated, PRIVILEGE_ACCESS))
            #logger.info('Allowing authenticated to access')
    
    def getitem(self, key):
        subs =  {
            'libraries': ResourceLibraries(),
            'shelves': ResourceShelves(),
            'exceptions': ResourceExceptionsJSON(),
            'exceptions_formatted': ResourceExceptionsFormatted(),
            'refresh': ResourceRefresh(),
            'exit': ResourceExit(),
            'login': ResourceLogin(),
            'logout': ResourceLogout(),
            'robots.txt': ResourceRobots(),
        }    
        return subs.get(key, None)
            
class ResourceExit(Resource): pass
class ResourceLogin(Resource): pass
class ResourceLogout(Resource): pass
        
class ResourceShelves(Resource):
    def getitem(self, key):
        return ResourceShelvesShelf(key)

    
class ResourceShelvesShelf(Resource):
    def getitem(self, key):
        subs =  {
            'subscribe': ResourceShelvesShelfSubscribe(self.name),
            'unsubscribe': ResourceShelvesShelfUnsubscribe(self.name),
        }    
        return subs.get(key, None)

class ResourceShelvesShelfSubscribe(Resource): pass
class ResourceShelvesShelfUnsubscribe(Resource): pass
class ResourceExceptionsFormatted(Resource): pass 
class ResourceExceptionsJSON(Resource): pass
class ResourceRefresh(Resource): pass 
    
class ResourceLibraries(Resource): 
    
    def getitem(self, libname):
        
        session = self.get_session()
        shelfname = session.get_shelf_for_libname(libname)
    
        r1 = ResourceShelf(shelfname)
        r1.__parent__ = self
        r2 = ResourceLibrary(libname)
        r2.__parent__ = r1
        
        print 'returning', r2.show_ancestors()
        return r2

class ResourceShelf(Resource): 
    
    def __init__(self, name):
        Resource.__init__(self, name)
        
    @property
    def __acl__(self):
        session = self.get_session()
        shelf = session.get_shelf(self.name)
        return shelf.get_acl().as_pyramid_acl()
        
    def getitem(self, key):
        return ResourceLibrary(key)
        
class ResourceLibrary(Resource): 
    
    def getitem(self, key):
        if key == 'refresh_library':
            return ResourceLibraryRefresh()
        if key == 'interactive':
            return ResourceLibraryInteractive()
        
        if key.endswith('.html'):
            docname = os.path.splitext(key)[0]
            return ResourceLibraryDocRender(docname)
        if '.' in key:
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
        self.specname = specname
        
    def getitem(self, key):
        if key == 'new': return ResourceThingsNewBase()
        return ResourceThing(key)
    
    def __repr__(self):
        return '%s(specname=%s)' % (type(self).__name__, self.specname)

    
class ResourceThingsNewBase(Resource):
    def getitem(self, key):
        return ResourceThingsNew(key)
    
class ResourceThingsNew(Resource):
    pass

class ResourceThing(Resource): 
    
    def getitem(self, key):
        subs =  {
            'views': ResourceThingViews('views'),
        }
        return subs.get(key, None)

class ResourceThingViews(Resource):
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
                'solver': ResourceThingViewSolver0(),
            }
            subs.update(**subs2)
            
        return subs.get(key, None)
    
class ResourceThingView(Resource): pass
class ResourceThingViewSyntax(ResourceThingView): pass
class ResourceThingViewDPGraph(ResourceThingView): pass
class ResourceThingViewDPTree(ResourceThingView): pass
class ResourceThingViewNDPGraph(ResourceThingView): pass
class ResourceThingViewNDPRepr(ResourceThingView): pass

class ResourceThingViewSolver(ResourceThingView): pass
class ResourceThingViewSolver0(ResourceThingView): pass

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
         

class ResourceRobots(Resource): pass

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

def context_get_library_name(context):
    library_name = get_from_context(ResourceLibrary, context).name
    return library_name

def context_get_library(context, request):
    from mcdp_web.main import WebApp
    app = WebApp.singleton
    session = app.get_session(request)
    library_name = context_get_library_name(context)
    library = session.get_library(library_name)
    return library

def context_get_spec(context):
    from mcdp_web.editor_fancy.app_editor_fancy_generic import specs
    specname = get_from_context(ResourceThings, context).specname
    spec = specs[specname]
    return spec

        
def context_get_widget_name(context):
    return get_from_context(ResourceThing, context).name
