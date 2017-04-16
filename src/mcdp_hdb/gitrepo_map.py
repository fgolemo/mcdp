from mcdp_utils_misc.fileutils import create_tmpdir
from mcdp_hdb.disk_struct import ProxyDirectory, ProxyFile
from contracts import contract
from git import Repo
from copy import deepcopy


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

@contract(disk_rep=ProxyDirectory, returns=ProxyDirectory)
def get_disk_rep_with_added_files(disk_rep):
    ''' Returns a new disk_rep where empty directories
        have a file called '.gitignore'. 
    '''
    DUMMY_FILE = '.gitignore'
    def map_d(d):
        d = deepcopy(d)
        if not d._files and not d._directories:
            d[DUMMY_FILE] = ProxyFile('ignore')
        for d2n, d2 in d._directories.items():
            d._directories[d2n] = map_d(d2) 
        return d
    return map_d(disk_rep)

@contract(disk_rep=ProxyDirectory)
def gitrep_from_diskrep(disk_rep, where=None, branch=None):
    ''' Creates a repository with the contents. '''
    if branch is None:
        branch = 'master'
    if where is None:
        where = create_tmpdir('gitrep_from_diskrep')
        
    repo = Repo.init(where)
    repo.index.commit('initial')
    head = repo.create_head(branch)
    head.checkout()
    if branch != 'master':
        repo.delete_head('master')
    d2 = get_disk_rep_with_added_files(disk_rep)
    d2.to_disk(where)
    
    if repo.untracked_files: 
        repo.index.add(repo.untracked_files)
    
#     modified_files = repo.index.diff(None)
#     for m in modified_files:
#         repo.index.add([m.b_path])
#         
#     author = Actor("system", "root@localhost")
    message = "gitrep_from_diskrep(%s)" % where
    repo.index.commit(message) #, author=author)
    return repo
    
@contract(repo=Repo)
def diskrep_from_gitrep(repo):
    working_tree_dir = repo.working_tree_dir
    if working_tree_dir is None:
        msg = 'This is a bare repository'
        raise ValueError(msg)

    diskrep = ProxyDirectory.from_disk(working_tree_dir)
    return diskrep

