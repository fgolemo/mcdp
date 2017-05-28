from contracts import contract
from mcdp.constants import MCDPConstants
from mcdp.logs import logger
from mcdp_hdb.gitrepo_map import create_empty_dir_from_schema
from mcdp_hdb.memdataview_utils import host_name
from mcdp_hdb.pipes import mount_git_repo, WriteToRepoCallback, mount_directory
from mcdp_hdb_mcdp.host_cache import HostCache
from mcdp_utils_misc import format_list
import os

from contracts.utils import raise_desc
from git.repo.base import Repo
from nose.tools import assert_equal

from .main_db_schema import DB


class HostInstance(object):
    ''' A MCDP server that participates in the co-design network. '''

    
    @contract(root=str, instance=str, upstream=str, repo_git='dict(str:str)', repo_local='dict(str:str)')
    def __init__(self, instance, upstream, root, repo_git, repo_local):
        '''
            root: where to put our temporary files
            repo_git: name -> remote git url
            repo_local: name -> local path
            
            As a special case, if name == 'user_db', then it is used as the users database.
            
            If no 'user_db' is passed, then we create an empty one inside root. 
        '''
        
        self.repos = {}
        self.who = {'host': host_name(), 'actor': 'system', 'instance': instance} 
        
        for name, dirname in repo_local.items():
            if not os.path.exists(dirname):
                msg = 'Directory %r for %r does not exist' % (dirname, name)
                raise_desc(ValueError, msg)
            
        self.repo_local = repo_local
        for repo_name, remote_url in repo_git.items():
            where = os.path.join(root, repo_name)
            logger.info('Loading %r = %r in dir %s' % (repo_name, remote_url, where)) 
            repo = Repo.init(where)
            origin = repo.create_remote('origin', url=remote_url)
            assert origin.exists()
            for _ in repo.remotes.origin.fetch(): pass
            # this is what we want to track: the branch "upstream"
            if not upstream in origin.refs:
                msg = 'Cannot track remote branch %r because it does not exist.' % upstream
                raise Exception(msg)
            
            # Do we already have a branch instance in the remote repo?
            if instance in origin.refs:
                # if so, check out
                logger.info('Checking out remote %r' % instance)
                head = repo.create_head(instance, origin.refs[instance])
                head.set_tracking_branch(origin.refs[instance])
                head.checkout()
            else:
                # we create it from the upstream branch
                logger.info('Creating local %s from remote %r' % (instance, upstream))
                head = repo.create_head(instance, origin.refs[upstream])
                head.checkout()
                logger.info('Pushing local %s' % (instance)) 
                repo.git.push('-u', 'origin', instance) 
                 
            self.repos[repo_name] = repo

        if not 'user_db' in self.repos and not 'user_db' in self.repo_local:
            dirname = os.path.join(root, 'user_db_local') 
            create_empty_dir_from_schema(dirname=dirname, schema=DB.user_db, disk_map=DB.dm)
            logger.info('No repository with name "user_db" passed. Creating empty one in %s' % dirname)
            self.repo_local['user_db'] = dirname
        self.mount()
        
        logger.info('Set up repositories %s.' % format_list(self.db_view.repos))
        for repo_name, repo in self.db_view.repos.items():
            logger.info('* repo %r has shelves %s ' % (repo_name, format_list(repo.shelves)))
        logger.info('Set up users %s.' % format_list(self.db_view.user_db.users))
        
        self.host_cache = HostCache(self.db_view)
        
    def mount(self):
        db_schema = DB.db
        db_data = db_schema.generate_empty()
        db_view = DB.view_manager.create_view_instance(db_schema, db_data)
        db_view._who = self.who
        db_view.set_root()
        self.db_view = db_view
        
        disk_map = DB.dm 
        view_repos = db_view.child('repos')
        
        for repo_name, dirname in self.repo_local.items():
            if repo_name == 'user_db':
                mount_directory(view0=db_view, child_name='user_db', disk_map=disk_map, dirname=dirname)
            else:
                mount_directory(view0=view_repos, child_name=repo_name, disk_map=disk_map, dirname=dirname)
            
                repo = view_repos[repo_name] 
            
        for repo_name, repo in self.repos.items():
            if repo_name == 'user_db':
                mount_git_repo(view0=db_view, child_name='user_db', disk_map=disk_map, repo=repo)
                this_view = db_view.child('user_db')
            else:
                mount_git_repo(view0=view_repos, child_name=repo_name, disk_map=disk_map, repo=repo)
                this_view = view_repos.child(repo_name)
                repo = view_repos[repo_name]
            assert this_view._notify_callback is not None
            #logger.info('callback for repo.%s: %s' % (repo_name, view_repo._notify_callback)
            PushCallback.add_to(this_view)
         
        all_repo_names = set(list(self.repos) + list(self.repo_local))
        all_repo_names.remove('user_db')
        
        assert_equal(id(view_repos), id(db_view.child('repos')))
        assert_equal(id(view_repos), id(db_view.repos))
        
        assert_equal(all_repo_names, set(view_repos))
        for repo_name in all_repo_names:
            view_repos[repo_name]
            db_view.repos[repo_name]
        
        username_anonymous = MCDPConstants.USER_ANONYMOUS
        if not username_anonymous in db_view.user_db.users:
            logger.info(('The user %r is not present in DB. '
                        'Creating one that is subscribed to everything') % username_anonymous)
            subscriptions = []
            for repo_name, repo in db_view.repos.items():
                subscriptions.extend(sorted(repo.shelves))
            info = dict(name='Anonymous User', username=username_anonymous, subscriptions=subscriptions)
            user = DB.user.generate_empty(info=info)
            db_view.user_db.users[username_anonymous] = user
        
    def set_local_permission_mode(self):
        ''' The anonymous user is renamed 'Local User' and given group admin. '''
        username_anonymous = MCDPConstants.USER_ANONYMOUS
        u = self.db_view.user_db.users[username_anonymous]
        u.info.name = 'Local user'
        u.info.groups.append('admin')
        
class PushCallback(object):
    @staticmethod
    def add_to(view):
        view._notify_callback = PushCallback(view._notify_callback)
    
    @contract(other=WriteToRepoCallback)
    def __init__(self, other):
        self.other = other
        
    def __call__(self, event):
        self.other(event)
        repo  = self.other.repo
        logger.debug('pushing')
        repo.remotes.origin.push()
        
        
#     hi_config = Schema()
#     
#     hi_config.string('root') # where to put temporary files
#     hi_config.string('instance') # instance name
#     hi_config.hash('repo_local', SchemaString()) # dirname for local repo
#     hi_config.hash('repo_git', SchemaString()) # git url for local repo
#      