from contracts import contract
from mcdp_user_db.user import UserInfo
from mcdp.constants import MCDPConstants
from abc import ABCMeta, abstractmethod
from mcdp_utils_misc.dir_from_package_nam import dir_from_package_name
from mcdp_shelf.shelves import find_shelves
from mcdp_utils_misc.fileutils import create_tmpdir
import os
from mcdp.logs import logger

class RepoException(Exception):
    pass


class RepoInvalidURL(RepoException):
    pass

class RepoChangeEvent():
    def when(self):
        pass
    def who(self):
        pass
    def what(self):
        pass


class MCDPRepo():
    ''' 
        An MCDP repo holds zero or more Bundles.
        
        Currently the only implementation is a git backend.
    '''
    
    __metaclass__ = ABCMeta
    
    @abstractmethod
    @contract(returns='dict(str:*)')
    def get_shelves(self):
        ''' Returns a dictionary of Bundles present in this repo. '''
        
    @abstractmethod
    def get_events(self, skip=0, max_events=None):
        ''' Returns a list of Repo Change Events '''
        
    @abstractmethod
    def get_desc_short(self):
        ''' Returns a short description. '''
    
    @abstractmethod
    def available(self):
        ''' Returns true if this is available. If not, then
            get the explanation using get_availability_error(). '''
    
    @abstractmethod
    def get_availability_error(self):
        ''' Explanation of why it is not available. '''
        
    
    @abstractmethod
    def checkout(self, where):
        ''' Checks out a local copy for remote repos. '''
    
    @abstractmethod
    @contract(user_info=UserInfo)
    def commit(self, user_info):
        ''' Commits the current information to the repository. '''
    
    @abstractmethod
    def push(self):
        ''' Pushes transactions '''
        
    @abstractmethod
    def pull(self):
        ''' Updates from remote location. '''
        
        
        
@contract(url=str, returns=MCDPRepo)    
def repo_from_url(url):
    '''
        Returns an MCDPRepo from a n url

        mcdpr:git:<git url>
        mcdpr:git:/filename
        mcdpr:git:git://github.com
        mcdpr:git:https://github.com/
        mcdpr:git:ssh://git@github.com/<user>/<repo>
        mcdpr:git:gh:<user>/<module>
        mcdpr:python:<module>
        mcdpr:pip:<egg>#name
            
    '''
    prefix = MCDPConstants.repo_prefix
    if not url.startswith(prefix):
        raise RepoInvalidURL(url)
    url0 = url[len(prefix):]
    delim = ':'
    if not delim in url0:
        msg = 'Cannot find schema delim in %r' % url0
        raise RepoInvalidURL(msg)
    i = url0.index(delim)
    schema = url0[:i]
    rest = url0[i+1:]
    if schema == 'git':
        return repo_from_url_git(rest)
    elif schema == 'pip':
        return repo_from_url_pip(rest)
    elif schema == 'python':
        return repo_from_url_python(rest)
    elif schema == 'gh':
        return repo_from_url_gh(rest)
    else:
        msg = 'Invalid schema %r in %r.' % (schema, url0)
        raise RepoInvalidURL(msg)

@contract(url=str, returns=MCDPRepo)    
def repo_from_url_gh(url):
    ''' gh:Username/repo '''
    
    if not '/' in url:
        msg = 'Expected gh:Username/repo'
        raise RepoInvalidURL(msg)
    
    i = url.index('/')
    username = url[i]
    repo = url[i+1:]
    
    url2 = 'git@github.com:%s/%s.git' % (username, repo)
    return MCDPGitRepo(url2)

@contract(url=str, returns=MCDPRepo)    
def repo_from_url_git(url):
    return MCDPGitRepo(url)
    
 
@contract(url=str, returns=MCDPRepo)    
def repo_from_url_pip(url):
    return MCDPPipRepo(url)
 
@contract(url=str, returns=MCDPRepo)    
def repo_from_url_python(url):
    return MCDPythonRepo(url)

from git import Repo

class MCDPGitRepo(MCDPRepo):
    def __init__(self, url, where=None, branch=None):
        '''
            where: local directory
        '''
        if where is None:
            where = create_tmpdir(prefix='git_repo')
            logger.debug('Created tmpdir %s' % where)
        else:
            if not os.path.exists(where):
                logger.debug('Created dir %s' % where)
                os.makedirs(where)
        
        # we have create the working dir
        assert os.path.exists(where)
        
        self.where = where
        self.repo = Repo(self.where)
        self.url = url
        
        
    def available(self):
        pass
    
    def get_availability_error(self):
        pass 
    
    def get_shelves(self):
        return self.shelves

    def get_events(self, skip=0, max_events=None):
        return []
    
    def get_desc_short(self):
        return 'Python package %r' % self.package
    
    def checkout(self, where):
        ''' Checks out a local copy for remote repos. '''
    
    def commit(self, user_info):
        return
    
    def push(self):
        return
    
    def pull(self):
        return
        
class MCDPPipRepo(MCDPRepo):
    def __init__(self, url):
        self.url = url
    
    def available(self):
        pass
    
    def get_availability_error(self):
        pass 
    
    def get_shelves(self):
        return self.shelves

    def get_events(self, skip=0, max_events=None):
        return []
    
    def get_desc_short(self):
        return 'Python package %r' % self.package
    
    def checkout(self, where):
        ''' Checks out a local copy for remote repos. '''
    
    def commit(self, user_info):
        return
    
    def push(self):
        return
    
    def pull(self):
        pass
    
class MCDPythonRepo(MCDPRepo):
    def __init__(self, package):
        self.package = package
        try:
            self.directory = dir_from_package_name(package)
        except ValueError:
            self.availability_error = 'Cannot find package "%s".' % package
            self.shelves = None
        else:
            self.shelves = find_shelves(self.directory)
            self.availability_error = None
    
    def available(self):
        return self.shelves is not None
    
    def get_availability_error(self):
        return self.availability_error 
    
    def get_shelves(self):
        return self.shelves

    def get_events(self, skip=0, max_events=None):
        return []
    
    def get_desc_short(self):
        return 'Python package %r' % self.package
    
    def checkout(self, where):
        ''' Checks out a local copy for remote repos. '''
    
    def commit(self, user_info):
        return
    
    def push(self):
        return
    
    def pull(self):
        return
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    