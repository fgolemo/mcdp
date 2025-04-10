# -*- coding: utf-8 -*-
from abc import abstractmethod, ABCMeta
import os

from contracts import contract
from contracts.utils import indent

from mcdp.logs import logger
from mcdp_utils_misc import memoize_simple, locate_files


class NoImageFound(Exception):
    pass

class ImagesSource(object):
    __metaclass__ = ABCMeta
    
    @abstractmethod
    @contract(returns=bytes, name=str, data_format=str)
    def get_image(self, name, data_format):
        ''' 
            Get an image with the given name.
        
            data_format: one of jpg,png,pdf,svg
            
            Raise NoImageFound if such image is not found. 
        '''
        
class NoImages(ImagesSource):
    def get_image(self, name, data_format):
        msg = f"NoImages: not found {name} {data_format}"
        raise NoImageFound(msg)
            
class ImagesFromPaths(ImagesSource):
    @contract(paths='seq(str)')
    def __init__(self, paths):
        self.paths = paths
        
    def get_image(self, name, data_format):
        extension = data_format
        for p in self.paths:
            for fn in _list_files_with_extension(p, extension):
                bn = os.path.basename(fn)
                x = os.path.splitext(bn)[0]
                
                if x.lower() == name.lower():
                    if x != name:
                        msg = f"Using file "{bn}" for image "{name}", even though case does not match."
                        _warn_once(msg)
                    
                    if os.path.exists(fn):
                        return open(fn).read()
                    else:
                        # warn broken link
                        msg = f"Filename does not exist (broken link?): {fn}"
                        logger.debug(msg)
                         
        msg = f"Could not find {name}.{data_format} in {len(self.paths} paths.")
        for p in self.paths:
            msg += f"\n path: {p}"
        raise NoImageFound(msg)

@memoize_simple
def _warn_once(msg):
    logger.warning(msg)
    
@memoize_simple
def _list_files_with_extension(dirname, extension):
    ''' List all files in the given directory with an extension.
        The result is cached. '''
    pattern = f"*.{extension}"
    res = list(locate_files(dirname, pattern))
    return res

class ImagesFromDB(ImagesSource):
    
    def __init__(self, db_view, subscribed_shelves, current_repo_name, current_shelf_name, current_library_name):
        self.db_view = db_view
        self.subscribed_shelves = subscribed_shelves
        self.current_repo_name = current_repo_name
        self.current_shelf_name = current_shelf_name
        self.current_library_name = current_library_name
        
    def get_image(self, name, data_format):
        # first try ours
        repos = self.db_view.repos
        repo = repos[self.current_repo_name]
        shelf = repo.shelves[self.current_shelf_name]
        library = shelf.libraries[self.current_library_name]
        images = library.images
        for candidate in images:
            if candidate.lower() == name.lower():
                if candidate != name:
                    msg = f"Using image "{candidate}" for "{name}" even though the name does not match."
                    _warn_once(msg)
        
                image = images[candidate]
                data = getattr(image, data_format)
                if data is not None:
                    return data
        
        # now try all of them
        for _repo_name, repo in repos.items():
            for shelf_name, shelf in repo.shelves.items():
                if not shelf_name in self.subscribed_shelves:
                    continue
                for _library_name, library in shelf.libraries.items():
                    images = library.images
                    if name in images:
                        image = images[name]
                        data = getattr(image, data_format)
                        if data is not None:
                            return data
        msg = f"Could not find image {name} {data_format}"
        raise NoImageFound(msg)
        
class TryMany(ImagesSource):
    
    def __init__(self, sources):
        self.sources = sources
        
    def get_image(self, name, data_format):
        errors = []
        for source in self.sources:
            try:
                return source.get_image(name, data_format)
            except NoImageFound as e:
                errors.append(e)
        msg = f"Could not find {name}.{data_format} in {len(self.sources} sources.")
        for i, e in enumerate(errors):
            msg += '\n' + indent(str(e), '%d> ' % i) 
        raise NoImageFound(msg)
        
        
