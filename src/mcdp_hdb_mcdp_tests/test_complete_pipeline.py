import os

from contracts import contract
from git.repo.base import Repo

from comptests.registrar import comptest, run_module_tests
from mcdp_hdb.disk_map import DiskMap
from mcdp_hdb.gitrepo_map import gitrep_from_diskrep, diskrep_from_gitrep
from mcdp_hdb_mcdp.main_db_schema import DB
from mcdp_repo.repo_interface import MCDPGitRepo
from mcdp_utils_misc.fileutils import create_tmpdir
from mcdp_hdb.memdataview import ViewMount

@contract(view0=ViewMount, child_name=str, disk_map=DiskMap, repo=Repo)
def mount_git_repo(view0, child_name, disk_map, repo):
    '''
        Mounts a repo -- just like "mount" in UNIX.
    '''
    # first, is the child well defined?
    child_schema = view0._schema.get_descendant((child_name,))
    # load the data in the repo
    disk_rep = diskrep_from_gitrep(repo)
    # is the data in the repo conformant to the schema?
    data = disk_map.interpret_hierarchy_(child_schema, disk_rep)
    # now create a view for this
    view_manager = view0._view_manager
    view = view_manager.create_view_instance(child_schema, data)
    view.set_root() # XXX
    view0.mount(child_name, view)
    
def create_empty_repo_from_schema(dirname, schema, disk_map):
    ''' Creates a git repo initialized with the empty data of the schema. '''
    # generate empty data
    data = schema.generate_empty()
    disk_rep = disk_map.create_hierarchy_(schema, data)
    repo = gitrep_from_diskrep(disk_rep, dirname)
    return repo

class Instance(object):
    
    def __init__(self, root, repos):
        assert 'user_db' in repos
        self.repos = {}
        for repo_name, remote_url in repos.items():
            where = os.path.join(root, repo_name)
            self.repos[repo_name] = MCDPGitRepo(url=remote_url, where=where)
        self.mount()
        
    def mount(self):
        db_data = {'repos':{}, 'user_db':{'users':{}}}
        db_schema = DB.db
        db_view = DB.view_manager.create_view_instance(db_schema, db_data)
        db_view.set_root()
        disk_map = DB.dm
        mount_git_repo(disk_map=disk_map, view0=db_view, child_name='user_db', repo=self.repos['user_db'].repo)
        for repo_name, mcdp_repo in self.repos.items():
            if repo_name != 'user_db':
                view_repos = db_view.child('repos')
                mount_git_repo(disk_map=disk_map, view0=view_repos, child_name=repo_name, repo=mcdp_repo.repo)
                
        # mount
        
class ComplicatedTestCase(object):
    def __init__(self, repos):
        ''' repos: names of repos to create ''' 
        self.root = create_tmpdir(prefix='test_pipeline1')
        self.repo_root = {} # repo_name -> directory
        
        for repo_name in repos:
            d = os.path.join(self.root, repo_name)
            self.repo_root[repo_name] = d  
            create_empty_repo_from_schema(dirname=d, schema=DB.repo, disk_map=DB.dm)
            
        user_db_dir = os.path.join(self.root, 'user_db')
        create_empty_repo_from_schema(dirname=user_db_dir, schema=DB.user_db, disk_map=DB.dm)
        self.repo_root['user_db'] = user_db_dir
        
        self.instances = {}
#         self.create_users_repo()
        
#     def create_users_repo(self):
#         # Create a view for this data
#         user_db_data = ComplicatedTestCase.get_user_db_data()
#         user_db_schema = DB.user_db
# #         user_db_view = DB.view_manager.create_view_instance(user_db_schema, user_db_data)
# #         user_db_view.set_root()
#         # write to disk 
#         disk_rep = DB.dm.create_hierarchy_(user_db_schema, user_db_data)
#         repo = gitrep_from_diskrep(disk_rep, self.repo_root['user_db'])
    
    
        
    def instance_clone(self, hostname):
        root = os.path.join(self.root, hostname)
        self.instances[hostname] = Instance(root=root, repos=self.repo_root)

        
#     @staticmethod
#     def get_user_db_data():
#         user_db = {
#             'users': {
#                 'andrea': {
#                     'images': {},
#                     'info': {
#                         'username': None,
#                     'email': None,
#                     'account_last_active': None,
#                     'account_created': None,
#                     'affiliation': None,
#                     'website': None,
#                     'name': 'Andrea',
#                     'groups': [],
#                     'subscriptions': [],
#                     'authentication_ids': [],
#                     }
#                 }
#             }
#         }
#         return user_db
#         db_data = {
#             'repos': {
#                 'repo1': {
#                     'shelves': {
#                     }
#                 }
#             },
#             'user_db': {
#                 
#             } 
#         }
#         return db_data

        
@comptest
def test_pipeline1():
    ''' 
        There is a remote repo
    '''
    # There is the "remote" repository
    tcs = ComplicatedTestCase(['repo1','repo2'])
    tcs.instance_clone('host1')
    tcs.instance_clone('host2')

if __name__ == '__main__':
    run_module_tests()