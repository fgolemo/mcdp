from pyramid.security import Allow, Authenticated, Everyone
import os


class Resource(object):
    
    def __init__(self, name):
        if isinstance(name,unicode):
            name = name.encode('utf-8')
        self.name = name
        
    def getitem(self, key):  # @UnusedVariable
        return None
    
    def __repr__(self):
        return '%s(%s)' % (type(self).__name__, self.name)
    
    def __getitem__(self, key):
        r = self.getitem(key)
        if r is None:
            print('asked for %r - not found' % key)
            raise KeyError(key)
        r.__parent__ = self
        print('asked for %r - returning %r ' % (key, r))
        return r

class MCDPResourceRoot(Resource):
    
    __acl__ = [
        (Allow, Authenticated, 'view'), 
        (Allow, Authenticated, 'edit'),
    ]
    
    def __init__(self, request):  # @UnusedVariable
        from mcdp_web.main import WebApp
        options = WebApp.singleton.options    # @UndefinedVariable
        if options.allow_anonymous:
            MCDPResourceRoot.__acl__.append((Allow, Everyone, 'access'))
            #logger.info('Allowing everyone to access')
        else:
            MCDPResourceRoot.__acl__.append((Allow, Authenticated, 'access'))
            #logger.info('Allowing authenticated to access')
    
    def getitem(self, key):
        subs =  {
            'libraries': ResourceLibraries('libraries'),
            'shelves': ResourceShelves('shelves'),
            'exceptions': ResourceExceptionsJSON('exceptions'),
            'exceptions_formatted': ResourceExceptionsFormatted('exceptions_formatted'),
            'refresh': ResourceRefresh('refresh'),
            'exit': ResourceExit('exit'),
        }    
        return subs.get(key, None)
            
class ResourceExit(Resource):
    pass
        
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

class ResourceShelvesShelfSubscribe(Resource):
    pass

class ResourceShelvesShelfUnsubscribe(Resource):
    pass


class ResourceExceptionsFormatted(Resource): pass 
class ResourceExceptionsJSON(Resource): pass

class ResourceRefresh(Resource): pass 
    
class ResourceLibraries(Resource): 
    
    def getitem(self, key):
        return ResourceLibrary(key)

class ResourceShelf(Resource): 
        
    def getitem(self, key):
        return ResourceLibrary(key)
        
class ResourceLibrary(Resource): 
    
    def getitem(self, key):
        if key == 'refresh_library':
            return ResourceLibraryRefresh('refresh_library')
        if key.endswith('.html'):
            docname = os.path.splitext(key)[0]
            return ResourceLibraryDocRender(docname)
        if '.' in key:
            return ResourceLibraryAsset(key)
        return ResourceThings(key)

class ResourceLibraryDocRender(Resource):
    pass
class ResourceLibraryAsset(Resource):
    pass

class ResourceLibraryRefresh(Resource):
    pass
    
class ResourceThings(Resource):
    def __init__(self, specname):
        self.specname = specname
        
    def getitem(self, key):
        return ResourceThing(key)
    
    def __repr__(self):
        return '%s(specname=%s)' % (type(self).__name__, self.specname)

    
class ResourceThing(Resource): 
    
    def getitem(self, key):
        subs =  {
            'views': ResourceThingViews('views'),
        }
        return subs.get(key, None)

class ResourceThingViews(Resource):
    def getitem(self, key):
        subs =  {
            'syntax': ResourceThingViewSyntax('syntax'),
            'edit_fancy': ResourceThingViewEditor('edit_fancy'),
            
        }
        if self.__parent__.__parent__.specname == 'models':
            subs2 = {
                'dp_graph': ResourceThingViewDPGraph('dp_graph'),
                'dp_tree': ResourceThingViewDPTree('dp_tree'),
                'ndp_graph': ResourceThingViewNDPGraph('ndp_graph'),
                'ndp_repr': ResourceThingViewNDPRepr('ndp_repr'),
                'solver2': ResourceThingViewSolver('solver2'),
            }
            subs.update(**subs2)
            
        return subs.get(key, None)
    
class ResourceThingView(Resource):
    pass
    
class ResourceThingViewSyntax(ResourceThingView): pass

class ResourceThingViewDPGraph(ResourceThingView): pass
class ResourceThingViewDPTree(ResourceThingView): pass
class ResourceThingViewNDPGraph(ResourceThingView): pass
class ResourceThingViewNDPRepr(ResourceThingView): pass

class ResourceThingViewSolver(ResourceThingView): pass

class ResourceThingViewEditor(ResourceThingView):
    def getitem(self, key): 
        subs =  {
            'ajax_parse': ResourceThingViewEditorParse('ajax_parse'),
            'save': ResourceThingViewEditorSave('save'),
        }
        return subs.get(key, None)
 

class ResourceThingViewEditorParse(Resource): pass
class ResourceThingViewEditorSave(Resource): pass


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
