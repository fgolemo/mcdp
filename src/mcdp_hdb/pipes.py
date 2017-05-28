from contracts import contract
from mcdp import logger
from mcdp_utils_misc import yaml_dump
import os

from contracts.utils import indent, raise_wrapped
from git.repo.base import Repo
from git.util import Actor

from .disk_map import DiskMap
from .disk_struct import ProxyDirectory
from .exceptions import HDBInternalError
from .gitrepo_map import diskrep_from_gitrep
from .memdataview import ViewMount
from .memdataview_utils import host_name


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
    view._who = view0._who
    view.set_root() # XXX
    apply_changes_to_disk_and_repo(disk_map=disk_map, view=view, wd=repo.working_dir)
    
    view0.mount(child_name, view)

@contract(view0=ViewMount, child_name=str, disk_map=DiskMap, dirname=str)
def mount_directory(view0, child_name, disk_map, dirname):
    '''
        Mounts a directory.
    '''
    child_schema = view0._schema.get_descendant((child_name,))
    # load the data in the repo
    disk_rep = ProxyDirectory.from_disk(dirname)
    # is the data in the repo conformant to the schema?
    data = disk_map.interpret_hierarchy_(child_schema, disk_rep)
    # now create a view for this
    view_manager = view0._view_manager
    try:
        view = view_manager.create_view_instance(child_schema, data)
    except TypeError as e:
        msg = 'Cannot mount_directory'
        msg += '\n' + indent(child_schema, 'child schema > ')
#         msg += '\n' + indent(yaml_dump(data), 'child data > ')
        raise_wrapped(HDBInternalError, e, msg)
    view._who = view0._who
    view.set_root() # XXX
    apply_changes_to_disk(disk_map=disk_map, view=view, dirname=dirname)
    view0.mount(child_name, view)

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


def apply_changes_to_disk(disk_map, view, dirname):
    ''' 
        Connects the view to a git repo by adding a callback
        that applies the changes to the disk and commits.
    '''
    callback = WriteToDiskCallback(dirname, disk_map, view)
    view._notify_callback = callback
    
def apply_changes_to_disk_and_repo(disk_map, view, wd):
    ''' 
        Connects the view to a git repo by adding a callback
        that applies the changes to the disk and commits.
    '''
    where = get_git_repo(wd)
    repo = Repo.init(where)
    callback = WriteToRepoCallback(repo, disk_map, view)
    view._notify_callback = callback
    

class WriteToDiskCallback(object):
    def __init__(self, dirname, disk_map, view):
        self.dirname = dirname
        self.disk_map = disk_map
        self.view = view 
        self.data_events = []
        
    def __repr__(self):
        return 'WriteToDiskCallback(%s; %s so far)' % (self.dirname, len(self.data_events))
         
    def __call__(self, data_event):
        from mcdp_hdb.disk_map_disk_events_from_data_events import disk_events_from_data_event
        from mcdp_hdb.disk_events import apply_disk_event_to_filesystem
        # A good one to debug
        # s = yaml_dump(data_event)
        # logger.debug('Event #%d:\n%s' % (len(self.data_events), indent(s, '> ')) )
        self.data_events.append(data_event)
        disk_events = disk_events_from_data_event(disk_map=self.disk_map, 
                                                 schema=self.view._schema, 
                                                 data_rep=self.view._data, 
                                                 data_event=data_event)
        
        for disk_event in disk_events:
            # logger.debug('Disk event:\n%s' % yaml_dump(disk_event))
            apply_disk_event_to_filesystem(self.dirname, disk_event)
            
    
class WriteToRepoCallback(object):
    def __init__(self, repo, disk_map, view):
        self.repo = repo
        self.disk_map = disk_map
        self.view = view 
        self.data_events = []
        
    def __repr__(self):
        return 'WriteToRepo(%s; %s so far)' % (self.repo.working_dir, len(self.data_events))
         
    def __call__(self, data_event):
        from mcdp_hdb.disk_map_disk_events_from_data_events import disk_events_from_data_event
        from mcdp_hdb.disk_events import apply_disk_event_to_filesystem
        s = yaml_dump(data_event)
        logger.debug('Event #%d:\n%s' % (len(self.data_events), indent(s, '> ')) )
        self.data_events.append(data_event)
        disk_events = disk_events_from_data_event(disk_map=self.disk_map, 
                                                 schema=self.view._schema, 
                                                 data_rep=self.view._data, 
                                                 data_event=data_event)
        
        for disk_event in disk_events:
            logger.debug('Disk event:\n%s' % yaml_dump(disk_event))
            wd = self.repo.working_dir
            apply_disk_event_to_filesystem(wd, disk_event, repo=self.repo)
            
        message = yaml_dump(data_event)
        who = data_event['who']
        if who is not None:
            actor = who['actor']
            host = who['host']
            instance = who['instance']
        else:
            actor = 'system'
            host = host_name()
            instance = 'unspecified'
            
        author = Actor(actor, '%s@%s' % (actor, instance))
        committer = Actor(instance, '%s@%s' % (instance, host))
        _commit = self.repo.index.commit(message, author=author, committer=committer)
        
        