from copy import deepcopy

from contracts import contract
from git import Repo
from git.util import Actor

from mcdp_utils_misc import create_tmpdir

from .disk_struct import ProxyDirectory, ProxyFile
from .memdataview_utils import host_name


def create_empty_dir_from_schema(dirname, schema, disk_map):
    data = schema.generate_empty()
    disk_rep = disk_map.create_hierarchy_(schema, data)
    disk_rep.to_disk(dirname)

def create_empty_repo_from_schema(dirname, schema, disk_map, branch=None):
    ''' Creates a git repo initialized with the empty data of the schema. '''
    # generate empty data
    data = schema.generate_empty()
    disk_rep = disk_map.create_hierarchy_(schema, data)
    repo = gitrep_from_diskrep(disk_rep, dirname, branch=branch)
    return repo

DUMMY_FILE = '.gitignore'
DUMMY_FILE_CONTENTS = 'ignore'

@contract(disk_rep=ProxyDirectory, returns=ProxyDirectory)
def get_disk_rep_with_added_files(disk_rep):
    ''' Returns a new disk_rep where empty directories
        have a file called DUMMY_FILE containing DUMMY_FILE_CONTENTS.
    '''
    def map_d(d):
        d = deepcopy(d)
        if not d._files and not d._directories:
            d[DUMMY_FILE] = ProxyFile(DUMMY_FILE_CONTENTS)
        for d2n, d2 in d._directories.items():
            d._directories[d2n] = map_d(d2) 
        return d
    return map_d(disk_rep)

@contract(disk_rep=ProxyDirectory, returns=ProxyDirectory)
def get_disk_rep_with_added_files_inverse(disk_rep):
    ''' Inverse of get_disk_rep_with_added_files():
        removes DUMMY_FILES. '''
    
    d0 = deepcopy(disk_rep)
    def remove_it(d):
        if DUMMY_FILE in d:
            d.file_delete(DUMMY_FILE)
        for dd in d.get_directories().values():
            remove_it(dd)
    remove_it(d0)
    return d0
    
    
@contract(disk_rep=ProxyDirectory)
def gitrep_from_diskrep(disk_rep, where=None, branch=None):
    ''' Creates a repository with the contents. '''
    if branch is None:
        branch = 'master'
    if where is None:
        where = create_tmpdir('gitrep_from_diskrep')
        
    repo = Repo.init(where)
    author = Actor("system", "system@%s" % host_name())
    repo.index.commit('initial commit', author=author, committer=author)
    head = repo.create_head(branch)
    head.checkout()
    if branch != 'master':
        repo.delete_head('master')
    d2 = get_disk_rep_with_added_files(disk_rep)
    d2.to_disk(where)
    
    if repo.untracked_files: 
        repo.index.add(repo.untracked_files)
     
    
    message = "gitrep_from_diskrep(%s)" % where
    repo.index.commit(message, author=author, committer=author)
    return repo
    
@contract(repo=Repo)
def diskrep_from_gitrep(repo):
    working_tree_dir = repo.working_tree_dir
    if working_tree_dir is None:
        msg = 'This is a bare repository'
        raise ValueError(msg)

    diskrep = ProxyDirectory.from_disk(working_tree_dir)
    diskrep = get_disk_rep_with_added_files_inverse(diskrep)
    return diskrep

