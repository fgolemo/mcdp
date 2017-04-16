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
from mcdp_library.specs_def import specs


class Instance(object):
    
    def __init__(self, inst_name, upstream, root, repo_git, repo_local):
        self.hi = HostInstance(inst_name=inst_name, upstream=upstream, root=root, repo_git=repo_git, repo_local=repo_local)
        
    def create_user(self, username):
        db_view = self.hi.db_view
        name = '%s %s' % (username, username)
        u = DB.user.generate_empty(info=dict(name=name))
        db_view.user_db.users[username] = u
        
    def create_shelf(self, repo_name, shelf_name):
        db_view = self.hi.db_view
        repo = db_view.repos[repo_name]
        if not shelf_name in repo.shelves:
            repo.shelves[shelf_name] = repo.shelves._schema.prototype.generate_empty()
        else:
            raise ValueError('already existing %r' % shelf_name)
        
    def create_library(self, repo_name, shelf_name, library_name):
        db_view = self.hi.db_view
        shelf = db_view.repos[repo_name].shelves[shelf_name]
        if not library_name in shelf.libraries:
            shelf.libraries[library_name] = shelf.libraries._schema.prototype.generate_empty()
        else:
            raise ValueError('already existing %r' % library_name)
        
    def create_thing(self, repo_name, shelf_name, library_name, spec_name, thing_name):
        db_view = self.hi.db_view
        spec = specs[spec_name]
        contents = spec.minimal_source_code
        library = db_view.repos[repo_name].shelves[shelf_name].libraries[library_name]
        things = library.things.child(spec_name)
        if not thing_name in things:
            things[thing_name] = contents
        else:
            msg = 'Already know thing %r' % thing_name
            raise ValueError(msg)
        
        
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
    host1 = tcs.instances['host1']
    host1.create_user('john')
    tcs.instances['host2'].create_user('jack')
    tcs.instances['host3'].create_user('pete')
    
    host1.create_shelf('repo1', 'shelfA')
    host1.create_library('repo1', 'shelfA', 'lib1')
    host1.create_thing('repo1', 'shelfA', 'lib1', 'models', 'model1')
    host1.create_thing('repo1', 'shelfA', 'lib1', 'posets', 'poset1')
    
        
if __name__ == '__main__':
    if len(sys.argv) > 1:
        root = sys.argv[-1]
        test_pipeline1(root)
    else:
        run_module_tests()