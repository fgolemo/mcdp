from abc import ABCMeta, abstractmethod
import os

from contracts import contract
from contracts.utils import raise_desc
from git import RemoteProgress
from git import Repo
from git.remote import Remote
from git.util import Actor

from mcdp import MCDPConstants
from mcdp.logs import logger
from mcdp_shelf import find_shelves
from mcdp_user_db import UserInfo
from mcdp_utils_misc import timeit_wall, create_tmpdir, dir_from_package_name


class RepoException(Exception):
    pass


class RepoInvalidURL(RepoException):
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
    def get_changes(self):
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


class MyProgressPrinter(RemoteProgress):
    def update(self, op_code, cur_count, max_count=None, message=''):
        print(op_code, cur_count, max_count, cur_count / (max_count or 100.0), message or "NO MESSAGE")
        pass
# end


class MCDPGitRepo(MCDPRepo):
    def __init__(self, url=None, where=None, desc_short=None):
        '''
            where: local directory
        '''
        self.desc_short = desc_short
        if where is None:
            where = create_tmpdir(prefix='git_repo')
            create = True
            logger.debug('Created tmpdir %s' % where)
        else:
            if not os.path.exists(where):
                logger.debug('Created dir %s' % where)
                os.makedirs(where)
                create = True
            else:
                create = False
        self.where = where
        if create:
            self.repo = Repo.init(self.where)
            if url is not None:
                origin = self.repo.create_remote('origin', url=url)
                assert origin.exists()
                for _fetch_info in self.repo.remotes.origin.fetch(progress=MyProgressPrinter()):
                    pass
                self.repo.create_head('master', origin.refs['master'])
                self.repo.heads.master.checkout()
        else:
            self.repo = Repo(self.where)
            origin = Remote(self.repo, 'origin')
            if not origin.exists():
                msg = 'The repo already exists but there is no "origin" remote.'
                raise_desc(ValueError, msg, remotes=list(self.repo.remotes))
                
            with timeit_wall('Fetching commits'):
                for _fetch_info in origin.fetch(progress=MyProgressPrinter()):
                    pass
        
        # we have create the working dir
        assert os.path.exists(where)
                 
        self.shelves = find_shelves(where)
        self.changes = []
        with timeit_wall('Loading commits'):
            for commit in self.repo.iter_commits(max_count=10):
                self._note_commit(commit)
            
#             print('author: %s' % commit.author)
#             print('authored_date: %s' % commit.authored_date)
#             print('committed_date: %s' % commit.committed_date)
#             print('committer: %s' % commit.committer)
#             print('message: %s' % commit.message)

            
        self.url = url
    
    def get_author(self, git_author):
        name = git_author.name
        if name == 'Andrea Censi':
            return 'andrea'
        username = git_author.email.split('@')[0]
        return username
    
    def _note_commit(self, commit):
        if not commit.parents:
            return
        for diff in commit.parents[0].diff(commit): 
            filename = diff.b_path
            components = filename.split('/')
            res = {}
            if diff.change_type == 'R100':continue
            res['change_type'] = diff.change_type
            res['filename'] = diff.b_path
            
            if os.path.basename(filename) in ['mcdpshelf.yaml', 'user.yaml', '.gitignore']:
                continue
            if 'mcdpweb_cache' in filename:
                continue
            
            for c in components:
                if MCDPConstants.shelf_extension in c:
                    res['shelf_name'] = os.path.splitext(c)[0]
                if MCDPConstants.library_extension in c:
                    res['library_name'] = os.path.splitext(c)[0]
                from mcdp_library.specs_def import specs
                for spec_name, spec in specs.items():
                    ext = spec.extension
                    if c.endswith('.'+ext):
                        res['spec_name'] = spec_name
                        res['thing_name'] = os.path.splitext(c)[0]
            author = self.get_author(commit.author)
            
            res['author'] = author
            res['date'] = commit.authored_date
            
            for k,v in res.items():
                if isinstance(v, unicode):
                    res[k] = v.encode('utf8')   
            
            if not 'thing_name' in res or not 'shelf_name' in res or not 'library_name' in res:
                #print('skipping %s' % res)
                pass
            else:
                # only show things that are current
                if not res['shelf_name'] in self.shelves:
                    exists = False
                    continue
                else:
                    shelf = self.shelves[res['shelf_name']]
                    if not res['library_name'] in shelf.get_libraries_path():
                        exists = False
                    else:
                        exists = True
                        
                res['exists'] = exists
                #print('change: %s' % res)
                self.changes.append(res)
            
    def get_changes(self):
        return self.changes
        
    def available(self):
        pass
    
    def get_availability_error(self):
        pass 
    
    def get_shelves(self):
        return self.shelves
 
    def get_desc_short(self):
        return self.desc_short
    
    def checkout(self, where):
        ''' Checks out a local copy for remote repos. '''
    
    def commit(self, user_info, message=''):
        with timeit_wall('commit'):
            author = user_info.as_git_actor()
            commit = repo_commit_all_changes(self.repo, message, author)
        if False:
            logger.debug('Not pushing')
            with timeit_wall('push'):
                self.repo.remotes.origin.push()
        self._note_commit(commit)
        
    def push(self):
        return
    
    def pull(self):
        return

def repo_commit_all_changes(repo, message=None, author=None):
    if author is None:
        author = Actor("me","me")
    if message is None:
        message = ""
    if repo.untracked_files: 
        repo.index.add(repo.untracked_files)
    
    modified_files = repo.index.diff(None)
    for m in modified_files:
        repo.index.add([m.b_path])
        
    commit = repo.index.commit(message, author=author)
    return commit
    
class MCDPPipRepo(MCDPRepo):
    def __init__(self, url):
        self.url = url
    
    def available(self):
        pass
    
    def get_availability_error(self):
        pass 
    
    def get_shelves(self):
        return self.shelves

    
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
    
    def get_changes(self):
        return []
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    