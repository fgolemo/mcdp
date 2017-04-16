import os

from comptests.registrar import comptest, run_module_tests
from mcdp_hdb.gitrepo_map import gitrep_from_diskrep
from mcdp_hdb_mcdp.host_instance import HostInstance
from mcdp_hdb_mcdp.main_db_schema import DB
from mcdp_utils_misc import create_tmpdir


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
        self.hi = HostInstance(root=root, repos=repos)
                 
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