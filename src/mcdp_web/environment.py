
from mcdp_shelf.access import USER_ANONYMOUS

from .resource_tree import ResourceRepo, get_from_context, ResourceLibrary, ResourceShelf, ResourceThings, ResourceThing, ResourceThingView


def cr2e(f):
    def f2(self, context, request):
        e = Environment(context, request)
        res = f(self, e)
        return res
    f2.__name__ = 'cr2e_%s' % f.__name__
    return f2

class Environment():
    def __init__(self, context, request):
        from mcdp_web.main import WebApp
        self.context = context
        self.request = request

        app = WebApp.singleton
        self.app = app
        self.session = app.get_session(request)
        rrepo = get_from_context(ResourceRepo, context)
        if rrepo is None:
            self.repo_name = None
            self.repo = None
        else:
            self.repo_name = rrepo.name
            self.repo = app.repos[self.repo_name]

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
            
        rview = get_from_context(ResourceThingView, context)
        self.view_name = rview.name if rview is not None else None
 
        self.user = self.session.get_user()
        # use username instead of authenticated_id
        self.username = None if self.user.username == USER_ANONYMOUS else self.user.username
        
        self.root = app.get_root_relative_to_here(request)
        