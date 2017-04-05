from mcdp_utils_misc.fileutils import create_tmpdir
from mcdp_hdb.disk_struct import ProxyDirectory
from contracts import contract
from git import Repo
from git.util import Actor


@contract(disk_rep=ProxyDirectory)
def gitrep_from_diskrep(disk_rep, where=None):
    ''' Creates a repository with the contents. '''
    
    if where is None:
        where = create_tmpdir('gitrep_from_diskrep')
        
    repo = Repo.init(where)
    
    disk_rep.to_disk(where)
    
    author = Actor("system","root@localhost")
    message = "initial commit"
    
    if repo.untracked_files: 
        repo.index.add(repo.untracked_files)
    
#     modified_files = repo.index.diff(None)
#     for m in modified_files:
#         repo.index.add([m.b_path])
#         
    repo.index.commit(message, author=author)
    return repo
    
@contract(repo=Repo)
def diskrep_from_gitrep(repo):
    working_tree_dir = repo.working_tree_dir
    if working_tree_dir is None:
        msg = 'This is a bare repository'
        raise ValueError(msg)

    diskrep = ProxyDirectory.from_disk(working_tree_dir)
    return diskrep