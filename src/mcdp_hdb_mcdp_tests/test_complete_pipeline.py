import os
import shutil
import sys

from comptests.registrar import comptest, run_module_tests
from mcdp_hdb_mcdp.host_instance import HostInstance
from mcdp_hdb_mcdp.main_db_schema import DB
from mcdp_utils_misc import create_tmpdir
from mcdp_hdb.gitrepo_map import create_empty_repo_from_schema,\
    create_empty_dir_from_schema
from copy import deepcopy


class Instance(object):
    
    def __init__(self, inst_name, upstream, root, repo_git, repo_local):
        self.hi = HostInstance(inst_name=inst_name, upstream=upstream, root=root, repo_git=repo_git, repo_local=repo_local)
        
    def create_user(self, username):
        db_view = self.hi.db_view
        name = '%s %s' % (username, username)
        u = DB.user.generate_empty(info=dict(name=name))
        db_view.user_db.users[username] = u
        
class ComplicatedTestCase(object):
    def __init__(self, repo_names, root=None, upstream=None):
        ''' repos: names of repos to create '''
        if upstream is None:
            upstream = 'upstream'
        self.upstream = upstream
        if root is None:
            root = create_tmpdir(prefix='test_pipeline1') 
        shutil.rmtree(root)
        os.makedirs(root)
        self.root = root
        self.repo_root = {} # repo_name -> directory
        
        for repo_name in repo_names:
            d = os.path.join(self.root, 'remotes', repo_name)
            create_empty_repo_from_schema(branch=upstream, dirname=d, schema=DB.repo, disk_map=DB.dm)
            self.repo_root[repo_name] = 'file://%s/.git' % os.path.abspath(d)
            
        user_db_dir = os.path.join(self.root, 'remotes', 'user_db')
        create_empty_repo_from_schema(branch=upstream, dirname=user_db_dir, schema=DB.user_db, disk_map=DB.dm)
        self.repo_root['user_db'] = 'file://%s/.git' % os.path.abspath(user_db_dir)
        
        self.instances = {} 
    
    def instance_clone(self, hostname, use_common_user_db):
        root = os.path.join(self.root, hostname)
        inst_name = hostname
        # add one local repository
        repo_local = {}
        repo_local['my_local'] = os.path.join(root, 'my_local')
        create_empty_dir_from_schema(dirname=repo_local['my_local'], schema=DB.repo, disk_map=DB.dm)
        repo_git = deepcopy(self.repo_root)
        # this forces the instance to create its own
        if not use_common_user_db:
            repo_git.pop('user_db')
        i = Instance(inst_name=inst_name, upstream=self.upstream, root=root, repo_git=repo_git, repo_local=repo_local)
        self.instances[hostname] = i

@comptest
def test_pipeline1(root=None):
    ''' 
        There is a remote repo
    '''
    # There is the "remote" repository
    tcs = ComplicatedTestCase(root=root, repo_names=['repo1','repo2'])
    tcs.instance_clone('host1', use_common_user_db=True)
    tcs.instance_clone('host2', use_common_user_db=True)
    tcs.instance_clone('host3', use_common_user_db=False)
    tcs.instances['host1'].create_user('john')
    tcs.instances['host2'].create_user('jack')
    tcs.instances['host3'].create_user('pete')
    
if __name__ == '__main__':
    if len(sys.argv) > 1:
        root = sys.argv[-1]
        test_pipeline1(root)
    else:
        run_module_tests()