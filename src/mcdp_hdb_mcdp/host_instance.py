import os

from mcdp_hdb.pipes import mount_git_repo
from mcdp_hdb_mcdp.main_db_schema import DB
from mcdp_repo.repo_interface import MCDPGitRepo


class HostInstance(object):
    ''' A MCDP server that participates in the network '''
    def __init__(self, root, repos):
        self.repos = {}
        for repo_name, remote_url in repos.items():
            where = os.path.join(root, repo_name)
            self.repos[repo_name] = MCDPGitRepo(url=remote_url, where=where)
        self.mount()
        
    def mount(self):
#         db_data = {'repos':{}, 'user_db':{'users':{}}}
        db_schema = DB.db
        db_data = db_schema.generate_empty()
        db_view = DB.view_manager.create_view_instance(db_schema, db_data)
        db_view.set_root()
        disk_map = DB.dm
        mount_git_repo(disk_map=disk_map, view0=db_view, child_name='user_db', repo=self.repos['user_db'].repo)
        for repo_name, mcdp_repo in self.repos.items():
            if repo_name != 'user_db':
                view_repos = db_view.child('repos')
                mount_git_repo(disk_map=disk_map, view0=view_repos, child_name=repo_name, repo=mcdp_repo.repo)
