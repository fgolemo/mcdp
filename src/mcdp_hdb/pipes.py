import os

from contracts.utils import indent
from git.repo.base import Repo
from git.util import Actor

from mcdp.logs import logger
from mcdp_hdb.memdataview_utils import host_name
from mcdp_utils_misc.my_yaml import yaml_dump


def get_git_repo(d, original_query=None):
    ''' Get the root directory for a repository given 
        one directory inside. '''
    if original_query is None:
        original_query = d
    if not d:
        msg = 'Could not find repo for %s' % original_query
        raise ValueError(msg)
    g = os.path.join(d, '.git')
    if os.path.exists(g):
        return d
    else:
        return get_git_repo(os.path.dirname(d), original_query)
    
def apply_changes_to_disk(disk_map, user_db_view, wd):
    where = get_git_repo(wd)
    repo = Repo.init(where)
#     hierarchy = ProxyDirectory.from_disk(wd)
    events = []
    def notify_callback(data_event):
        from mcdp_hdb.disk_map_disk_events_from_data_events import disk_events_from_data_event
        from mcdp_hdb.disk_events import apply_disk_event_to_filesystem
        s = yaml_dump(data_event)
        logger.debug('Event #%d:\n%s' % (len(events), indent(s, '> ')) )
        events.append(data_event)
        disk_events = disk_events_from_data_event(disk_map=disk_map, 
                                                 schema=user_db_view._schema, 
                                                 data_rep=user_db_view._data, 
                                                 data_event=data_event)
        
        for disk_event in disk_events:
            logger.debug('Disk event:\n%s' % yaml_dump(disk_event))
            apply_disk_event_to_filesystem(wd, disk_event, repo=repo)
            
        message = yaml_dump(data_event)
        who = data_event['who']
        if who is not None:
            actor = who['actor']
            system = who['host']['hostname']
        else:
            actor = 'system'
            system = host_name()
        author = Actor(actor, None)
        committer = Actor(system, None)
#         logger.debug('2) all added')
#         system_cmd_show(wd, ['git', 'status'])
        commit = repo.index.commit(message, author=author, committer=committer)
#         commits.append(commit)
            
    user_db_view._notify_callback = notify_callback