# -*- coding: utf-8 -*-
import os

from contracts import contract
from contracts.utils import raise_desc, check_isinstance
from mcdp import MCDPConstants, logger
from mcdp.exceptions import DPSemanticError

from .library import MCDPLibrary
from .utils import locate_files
from mcdp_library.utils.dir_from_package_nam import dir_from_package_name


__all__ = [
    'Librarian',
]


class Librarian():
    
    """ 
        Indexes several libraries. 
        
        A hook is created so that each one can find the others.
           
            l = Librarian()
            l.find_libraries(dirname)
            lib = l.load_library('short') # returns MCDPLibrary
    """

    def __init__(self):
        self.libraries = {}
    
    @contract(returns='dict(str:dict)')
    def get_libraries(self):
        """ Returns dict libname => dict(path, library:MCDPLibrary) """
        return self.libraries
    
    @contract(dirname=str, returns='None')
    def find_libraries(self, dirname):
        if is_python_module_name(dirname):
            package = dir_from_package_name(dirname)
            logger.info('%s -> %s' % (dirname, package))
            dirname = package

        if dirname.endswith('.mcdplib'):
            libraries = [dirname]
        else:
            libraries = locate_files(dirname, "*.mcdplib",
                                 followlinks=False,
                                 include_directories=True,
                                 include_files=False)
            if not libraries:
                # use dirname as library path
                libraries = [dirname]
        
        for path in libraries:
            self.add_lib_by_path(path)
            
        # get all the images
        allimages = {} # base.ext -> same struct as l.file_to_contents
        for short, data in self.libraries.items():
            l = data['library']
            for ext in MCDPConstants.exts_images:
                basenames = l._list_with_extension(ext)
#                 print('basenames: for %s are  %s' % (ext, basenames))
                for b in basenames:
                    b_ext = b + '.' + ext
#                     print('b_Ext: %s b_Ext in ftc: %s' % (b_ext, b_ext in l.file_to_contents))
#                     if not b_ext in l.file_to_contents:
#                         print 'avialable: %s' % sorted(l.file_to_contents)
                    allimages[b_ext] = l.file_to_contents[b_ext]
                    
        for short, data in self.libraries.items():
            l = data['library']
            for basename, d in allimages.items():
                if not basename in l.file_to_contents:
                    l.file_to_contents[basename] = d

    def add_lib_by_path(self, path):
        short, data = self._load_entry(path)
        if short in self.libraries:
            entry = self.libraries[short]
            if entry['path'] != data['path']:
                msg = 'I already know library "%s".\n' % short
                msg += 'Current entry path:  %s\n' % data['path']
                msg += 'Previous entry path: %s\n' % entry['path']
                raise_desc(ValueError, msg)
            else:
                msg = 'Reached library "%s" twice (path = %s).' % (short, path)
                logger.debug(msg)
        self.libraries[short] = data
        
    @contract(dirname=str, returns='tuple(str, dict)')
    def _load_entry(self, dirname):
        if dirname == '.':
            dirname = os.path.realpath(dirname)
            
        dirname = os.path.realpath(dirname)
        library_name = os.path.splitext(os.path.basename(dirname))[0]
        library_name = library_name.replace('.', '_')

        load_library_hooks = [self.load_library]
        l = MCDPLibrary(load_library_hooks=load_library_hooks)
        l.add_search_dir(dirname)

        data = dict(path=dirname, library=l)
        l.library_name = library_name
        return library_name, data
        
    @contract(libname=str, returns='isinstance(MCDPLibrary)')
    def load_library(self, libname, context=None):  # @UnusedVariable
        check_isinstance(libname, str)
        """ hook to pass to MCDPLibrary instances to find their sisters. """
        if not libname in self.libraries:
            s = ", ".join(sorted(self.libraries))
            msg = 'Cannot find library %r. Available: %s.' % (libname, s)
            raise_desc(DPSemanticError, msg)
        l = self.libraries[libname]['library']
        return l
     
    @contract(returns='isinstance(MCDPLibrary)')
    def get_library_by_dir(self, dirname):
        """ 
            Returns the library corresponding to the dirname, 
            if it was already loaded.
            
            Otherwise a new MCDPLibrary is created. 
        """
        rp = os.path.realpath
        # check if it is already loaded
        for _short, data in self.libraries.items():
            if rp(data['path']) == rp(dirname):
                return data['library']
        # otherwise load it
        # Note this does not add it to the list
        _short, data = self._load_entry(dirname)
        data['library'].library_name = _short
        return data['library']

@contract(returns='dict(str:str)')
def find_libraries(d0):
    '''
        Finds <name>.mcdplib.
        returns dict ID -> path
    '''
    dirs = locate_files(d0, "*.mcdplib",
                                 followlinks=False,
                                 include_directories=True,
                                 include_files=False)
    res = {}
    for dirname in dirs:
        if dirname == '.':
            dirname = os.path.realpath(dirname)
        library_name = os.path.splitext(os.path.basename(dirname))[0]
        library_name = library_name.replace('.', '_')
        res[library_name] = dirname
    return res

def is_python_module_name(x):
    from pkgutil import iter_modules
    return x in (name for loader, name, ispkg in iter_modules())
    