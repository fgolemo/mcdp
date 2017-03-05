from mcdp_web.resource_tree import get_from_context, ResourceLibrary,\
    ResourceShelf, ResourceThings, ResourceThing

class Environment():
    def __init__(self, context, request):
        from mcdp_web.main import WebApp
        self.context = context
        self.request = request

        app = WebApp.singleton
        self.app = app
        self.session = app.get_session(request)
        rlibrary = get_from_context(ResourceLibrary, context)
        if rlibrary is None:
            self.library_name = None
            self.library = None
        else:            
            self.library_name = rlibrary.name 
            self.library = self.session.get_library(self.library_name)
        
        rshelf = get_from_context(ResourceShelf, context)
        if rshelf is None:
            self.shelf_name = None
            self.shelf = None
        else:            
            self.shelf_name = rshelf.name 
            self.shelf = self.session.get_shelf(self.shelf_name)
            
        from mcdp_web.editor_fancy.app_editor_fancy_generic import specs
        rspec = get_from_context(ResourceThings, context)
        if rspec is None:
            self.spec_name = None
            self.spec = None
        else:
            self.spec_name = rspec.specname
            self.spec = specs[self.spec_name]
    
        rthing = get_from_context(ResourceThing, context)
        if rthing is None:
            self.thing_name = None
        else:
            self.thing_name = rthing.name

        self.user = self.session.get_user()