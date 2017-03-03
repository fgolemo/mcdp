from pyramid.security import Allow, Authenticated, Everyone


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
        }    
        return subs.get(key, None)
            
    
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

    
class ResourceLibraries(Resource): 
    
    def getitem(self, key):
        return ResourceLibrary(key)

class ResourceShelf(Resource): 
        
    def getitem(self, key):
        return ResourceLibrary(key)
        
class ResourceLibrary(Resource): 
    
    def getitem(self, key):
        return ResourceThings(key)

    
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
            'views': ResourceThingViews,
        }
        if key in subs:
            return subs[key](key)

class ResourceThingViews(Resource):
    def getitem(self, key):
        subs =  {
            'syntax': ResourceThingViewSyntax,
            'edit_fancy': ResourceThingViewEditor,
            
        }
        if self.__parent__.__parent__.specname == 'models':
            subs2 = {
                'dp_graph': ResourceThingViewDPGraph,
                'dp_tree': ResourceThingViewDPTree,
                'ndp_graph': ResourceThingViewNDPGraph,
                'ndp_repr': ResourceThingViewNDPRepr,
                'solver2': ResourceThingViewSolver,
            }
            subs.update(**subs2)
            
        if key in subs:
            return subs[key](key)
    
class ResourceThingView(Resource):
    pass
    
class ResourceThingViewSyntax(ResourceThingView): pass

class ResourceThingViewDPGraph(ResourceThingView): pass
class ResourceThingViewDPTree(ResourceThingView): pass
class ResourceThingViewNDPGraph(ResourceThingView): pass
class ResourceThingViewNDPRepr(ResourceThingView): pass

class ResourceThingViewSolver(ResourceThingView): pass

class ResourceThingViewEditor(ResourceThingView):
    def getkey(self, key): 
        subs =  {
            'parse': ResourceThingViewEditorParse,
        }
        if key in subs:
            return subs[key](key)
 

class ResourceThingViewEditorParse(Resource): 
    pass


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
