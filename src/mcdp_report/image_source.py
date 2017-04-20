# -*- coding: utf-8 -*-
from abc import abstractmethod, ABCMeta
import os

from contracts import contract
from contracts.utils import indent

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
        msg = 'NoImages: not found %s %s' % (name, data_format)
        raise NoImageFound(msg)
            
class ImagesFromPaths(ImagesSource):
    @contract(paths='seq(str)')
    def __init__(self, paths):
        self.paths = paths
        
    def get_image(self, name, data_format):
        extension = data_format
        for p in self.paths:
            fn = os.path.join(p, '%s.%s' % (name, extension))
            if os.path.exists(fn):
                return open(fn).read()
        msg = 'Could not find %s.%s in %d paths.' % (name, data_format, len(self.paths))
        for p in self.paths:
            msg += '\n path: %s' % p
        raise NoImageFound(msg)

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
        if name in images:
            image = images[name]
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
        msg = 'Could not find image %s %s' % (name, data_format)
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
        msg = 'Could not find %s.%s in %d sources.' % (name, data_format, len(self.sources))
        for i, e in enumerate(errors):
            msg += '\n' + indent(str(e), '%d> ' % i) 
        raise NoImageFound(msg)
        
        
