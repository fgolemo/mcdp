from contracts import contract
from contracts.utils import raise_desc
from mcdp_library.libraries import Librarian
import os
from mcdp.utils.natsort import natural_sorted

class Session():
    
    def __init__(self, request, dirname):
        self.request = request
        self._load_libraries(dirname)
        
    def set_last_request(self, request):
        self.request = request

    def _load_libraries(self, dirname):
        """ Loads libraries in the "self.dirname" dir. """
        self.librarian = Librarian()
        self.librarian.find_libraries(dirname)
        self.libraries = self.librarian.get_libraries()
        for _short, data in self.libraries.items():
            l = data['library']
            path = data['path']
            cache_dir = os.path.join(path, '_cached/mcdpweb_cache')
            l.use_cache_dir(cache_dir)
    
    @contract(returns='list(str)')
    def list_libraries(self):
        """ Returns the list of libraries """
        return sorted(self.libraries)

    @contract(returns=str)
    def get_current_library_name(self):
        library_name = str(self.request.matchdict['library'])  # unicod
        return library_name

    def get_library(self):
        library_name = self.get_current_library_name()
        if not library_name in self.libraries:
            msg = 'Could not find library %r.' % library_name
            raise_desc(ValueError, msg, available=self.libraries)
        return self.libraries[library_name]['library']

    def refresh_libraries(self):
        for l in [_['library'] for _ in self.libraries.values()]:
            l.delete_cache()

        from mcdp_report.gdc import get_images
        assert hasattr(get_images, 'cache')  # in case it changes later
        get_images.cache = {}
        
    def get_libraries_indexed_by_dir(self):
        """
            returns a list of tuples (dirname, list(libname))
        """
        from collections import defaultdict
        path2libraries = defaultdict(lambda: [])
        for libname, data in self.libraries.items():
            path = data['path']
            sup = os.path.basename(os.path.dirname(path))
            path2libraries[sup].append(libname)
                     
        res = []
        for sup in natural_sorted(path2libraries):
            r = (sup, natural_sorted(path2libraries[sup]))
            res.append(r)
        return res 
    
    