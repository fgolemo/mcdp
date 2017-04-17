from mcdp_library.library import MCDPLibrary
from contextlib import contextmanager
from mocdp.comp.context import Context
from contracts import contract
from mcdp_utils_misc.string_utils import format_list
from mcdp.exceptions import DPSemanticError
from contracts.utils import raise_desc
from mcdp_library.specs_def import specs


__all__ = [
    'LibraryView',
]

class LibraryView():
    pass 


class TheContext(Context):
    
    def __init__(self, db_view, subscribed_shelves, current_library_name):
        self.db_view = db_view
        self.subscribed_shelves = subscribed_shelves
        self.current_library_name = current_library_name
        Context.__init__(self)
        self.load_ndp_hooks = [self.load_ndp]
        self.load_posets_hooks = [self.load_poset]
        self.load_primitivedp_hooks = [self.load_primitivedp]
        self.load_template_hooks = [self.load_template]
        self.load_library_hooks = [self.load_library]

    def load_library(self, library_name, context=None):
        repos = self.db_view.repos
        for repo_name, repo in repos.items():
            for shelf_name in self.subscribed_shelves:
                if shelf_name in repo.shelves:
                    shelf = repo.shelves[shelf_name]
                    if library_name in shelf.libraries:
                        return self.make_library(repo_name, shelf_name, library_name)
        msg = 'Could not find library %r.' % library_name
        raise ValueError(msg)
    
    @contract(returns=MCDPLibrary)
    def make_library(self, repo_name, shelf_name, library_name): 
        l = TheContextLibrary(self, repo_name, shelf_name, library_name)
        return l
    
    def get_library(self):
        return self.load_library(self.current_library_name)
    
    def load_ndp(self, name, context=None):
        return self.get_library().load_ndp(name, context)
    
    def load_poset(self, name, context=None):
        return self.get_library().load_poset(name, context)
    
    def load_primitivedp(self, name, context=None):
        return self.get_library().load_primitivedp(name, context)
    
    def load_template(self, name, context=None):
        return self.get_library().load_template(name, context)
    
        
class TheContextLibrary(MCDPLibrary):
    
    @contract(the_context=TheContext)
    def __init__(self, the_context, repo_name, shelf_name, library_name):
        self.the_context = the_context
        self.repo_name = repo_name
        self.shelf_name = shelf_name
        self.library_name = library_name
        MCDPLibrary.__init__(self)
        
    def _generate_context_with_hooks(self):
        return self.the_context
      
    def _load_spec_data(self, spec_name, thing_name):
        shelf = self.the_context.db_view.repos[self.repo_name].shelves[self.shelf_name]
        library = shelf.libraries[self.library_name]
        things = library.things.child(spec_name)
        if not thing_name in things:
            msg = 'Could not find %r in %s.' % (thing_name, spec_name)
            available = sorted(things)

            if available:
                msg += (" Available %s: %s." %
                        (spec_name, format_list(sorted(available))))
            else:
                msg += " None of those found."
                
            raise_desc(DPSemanticError, msg)
        else:
            data = things[thing_name]
            spec = specs[spec_name]
            basename  = thing_name + '.' + spec.extension
            realpath = '%s in library %r in shelf %r in repo %r' % (basename, self.library_name,
                                                                    self.shelf_name, self.repo_name) 
            return dict(data=data, realpath=realpath)
    
    def clone(self):
        return self
    
    @contextmanager
    def _sys_path_adjust(self):
        yield
        