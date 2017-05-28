from collections import OrderedDict
from copy import deepcopy
import os
import shutil

from contracts import contract, new_contract
from contracts.utils import check_isinstance, indent, raise_wrapped

from mcdp.logs import logger
from mcdp_utils_misc import yaml_dump

from .disk_errors import InvalidDiskOperation
from .disk_struct import ProxyDirectory, ProxyFile


class DiskEvents(object):
    dir_create = 'dir_create' # <dirname> <name>
    dir_rename = 'dir_rename' # <dirname> <name> <name2>
    dir_delete = 'dir_delete' # <dirname> <name> 
    file_create = 'file_create' # <dirname> <name> <contents>
    file_modify = 'file_modify' # <dirname> <name> <contents>
    file_delete = 'file_delete' #  <dirname> <name>
    file_rename = 'file_rename' #  <dirname> <name> <name2>
    disk_event_group = 'disk_event_group' # <events>
    all_events = [dir_rename, dir_delete, dir_create,
                  file_create, file_modify, file_delete, file_rename, disk_event_group] 

def ff(f):
    @contract(_id=str, who='assert_valid_who')
    def f2(_id, who, *args, **kwargs):
        check_isinstance(_id, str)
        #logger.debug('Calling %s with args = %s kwargs = %s' % (f, args, kwargs))
        event_name, arguments = f(*args, **kwargs)
        e =  disk_event_make(_id, event_name, who, arguments)
        return e
    return f2


@new_contract
@contract(x='seq(str)')
def valid_dirname(x):
    ''' Checks that it is a sequence of strings - not None '''
    if None in x:
        msg = 'Invalid dirname %s' % x.__repr__()
        raise ValueError(msg) 
    for c in x:
        if c == '':
            msg = 'Invalid component in %s' %str(x)
            raise ValueError(msg)
     
@ff
def disk_event_disk_event_group(events):
    if not events:
        msg = 'Group with no events?'
        raise ValueError(msg)
    assert len(events) >= 1
    return DiskEvents.disk_event_group, dict(events=deepcopy(events))

def disk_event_disk_event_group_interpret(disk_rep, events):
    for event in events:
        disk_event_interpret(disk_rep, event)
        
@ff
@contract(dirname='valid_dirname')
def disk_event_dir_create(dirname, name):
    return DiskEvents.dir_create, dict(dirname=dirname, name=name)

def disk_event_dir_create_interpret(disk_rep, dirname, name):
    d = get_dir(disk_rep, dirname)
    if name in d:
        msg = 'Cannot create directory "%s" that already exists' % name
        if True:
            logger.warn(msg)
        else:
            raise InvalidDiskOperation(msg)
    else:
        d[name] = ProxyDirectory()

@ff
@contract(dirname='valid_dirname')
def disk_event_dir_rename(dirname, name, name2):
    return DiskEvents.dir_rename, dict(dirname=dirname, name=name, name2=name2)

def disk_event_dir_rename_interpret(disk_rep, dirname, name, name2):
    d = get_dir(disk_rep, dirname)
    d.dir_rename(name, name2)

@ff
@contract(dirname='valid_dirname')
def disk_event_dir_delete(dirname, name):
    return DiskEvents.dir_delete, dict(dirname=dirname, name=name)

def disk_event_dir_delete_interpret(disk_rep, dirname, name):
    d = get_dir(disk_rep, dirname)
    d.dir_delete(name)


@ff
@contract(dirname='valid_dirname', name=str, contents=str)
def disk_event_file_create(dirname, name, contents):
    return DiskEvents.file_create, dict(dirname=dirname, name=name, contents=contents)

def disk_event_file_create_interpret(disk_rep, dirname, name, contents):
    d = get_dir(disk_rep, dirname)
    d.file_create(name, contents)

    
@ff
@contract(dirname='valid_dirname')
def disk_event_file_modify(dirname, name, contents):
    return DiskEvents.file_modify, dict(dirname=dirname, name=name, contents=contents)

def disk_event_file_modify_interpret(disk_rep, dirname, name, contents):
    d = get_dir(disk_rep, dirname)
    d.file_modify(name, contents)

@contract(dirname='valid_dirname')
def get_dir(disk_rep, dirname):
    # remove None components
    d = disk_rep.get_descendant(dirname)
    if isinstance(d, ProxyFile):
        msg = 'Dirname %r corresponds to ProxyFile, not dir.' % (d)
        raise ValueError(msg)
    return d

@ff
@contract(dirname='valid_dirname')
def disk_event_file_delete(dirname, name):
    return DiskEvents.file_delete, dict(dirname=dirname, name=name)

def disk_event_file_delete_interpret(disk_rep, dirname, name):
    d = get_dir(disk_rep, dirname)
    d.file_delete(name)
 
@ff
@contract(dirname='valid_dirname')
def disk_event_file_rename(dirname, name, name2):
    return DiskEvents.file_rename, dict(dirname=dirname, name=name, name2=name2)

def disk_event_file_rename_interpret(disk_rep, dirname, name, name2):
    d = get_dir(disk_rep, dirname)
    d.file_rename(name, name2)

def disk_event_make(_id, event_name, who, arguments):
    assert event_name in DiskEvents.all_events, event_name
    d = OrderedDict()
    d['id'] = _id
    d['operation'] = event_name
    d['who'] = who
    d['arguments']=arguments
    return d
 

@contract(disk_rep=ProxyDirectory)
def disk_event_interpret(disk_rep, disk_event):
    fs = {
        DiskEvents.disk_event_group: disk_event_disk_event_group_interpret,
        DiskEvents.dir_create: disk_event_dir_create_interpret,
        DiskEvents.dir_rename: disk_event_dir_rename_interpret,
        DiskEvents.dir_delete: disk_event_dir_delete_interpret,
        DiskEvents.file_create: disk_event_file_create_interpret,
        DiskEvents.file_modify: disk_event_file_modify_interpret,
        DiskEvents.file_delete: disk_event_file_delete_interpret,
        DiskEvents.file_rename: disk_event_file_rename_interpret,
    }
    ename = disk_event['operation']
    if not ename in fs:
        raise NotImplementedError(ename)
    intf = fs[ename]
    arguments = disk_event['arguments']
    try:
        logger.info('%s %s' % (ename, arguments))
        intf(disk_rep=disk_rep, **arguments)
    except Exception as e:
        msg = 'Could not complete the replay of this event: \n'
        msg += indent(yaml_dump(disk_event), 'disk_event: ')
        msg += '\nFor this tree:\n'
        msg += indent((disk_rep.tree()), ' disk_rep: ')
        from mcdp_hdb.memdataview import InvalidOperation
        raise_wrapped(InvalidOperation, e, msg)


def apply_disk_event_to_filesystem(wd, disk_event, repo=None):
    '''
        Applies the disk events to the filesystem.
        
        If repo is not None, it applies the changes to the index as well.
    '''  
    if repo:
        repo_index = repo.index
    else:
        repo_index = None
        
    def path_relative_to_repo(fn):
        repo_dir = repo.working_dir
        x = os.path.relpath(fn, repo_dir)
#         logger.debug('%s %s - > %s ' % (repo_dir, fn, x))
        return x
    
    def descendants_tracked(dirname):
        ''' Yields absolute, relative (to dirname) '''
        def tracked(absolute_fn):  # @UnusedVariable
            return True # XXX
        for root, _, files in os.walk(dirname, followlinks=False):
            for f in files:
                absolute = os.path.join(root, f)
                if tracked(absolute):
                    yield absolute, f
        
    def as_path(dirname, sub):
        path = os.path.join(wd, '/'.join(dirname))
        res = os.path.join(path, sub)
        return res 
    
    def dir_create(dirname, name):
        p = as_path(dirname, name)
        os.makedirs(p)
        
    def dir_rename(dirname, name, name2):
        p1 = as_path(dirname, name)
        p2 = as_path(dirname, name2)
        os.rename(p1, p2)
        if repo_index:
            for _, rel in descendants_tracked(p1):
#                 fn1 = path_relative_to_repo(os.path.join(p1, rel))
#                 fn2 = path_relative_to_repo(os.path.join(p2, rel))
                f1 = os.path.join(p1, rel)
                f2 = os.path.join(p2, rel)
                repo_index.move([f1, f2])
        
    def file_rename(dirname, name, name2):
        p1 = as_path(dirname, name)
        p2 = as_path(dirname, name2)
        if repo_index:
#             fn1 = path_relative_to_repo(p1)
#             fn2 = path_relative_to_repo(p2)
#             logger.debug('fn1: %s' % fn1)
#             logger.debug('fn2: %s' % fn2)
#             # repo_index.move(fn1, fn2)
#             logger.debug('working dir: %s' % repo.working_dir)
#             logger.debug('p1: %s' % p1)
#             logger.debug('p2: %s' % p2)
            repo_index.move([p1, p2])
        else:
            os.rename(p1, p2)
        
    def dir_delete(dirname, name):
        p = as_path(dirname, name)
        shutil.rmtree(p) 
        if repo_index:
            for absolute, _rel in descendants_tracked(p):
                fn = path_relative_to_repo(absolute)
                repo_index.remove([fn])
        
    def file_create(dirname, name, contents):
        p = as_path(dirname, name)
        with open(p, 'wb') as f:
            f.write(contents)
        if repo_index:
            fn  = path_relative_to_repo(p)
            repo_index.add([fn])
    
    def file_modify(dirname, name, contents):
        p = as_path(dirname, name)
        with open(p, 'wb') as f:
            f.write(contents)
        if repo_index:
            fn  = path_relative_to_repo(p)
            repo_index.add([fn])
    
    def file_delete(dirname, name):
        p = as_path(dirname, name)
        os.unlink(p)
        if repo_index:
            fn = path_relative_to_repo(p)
            repo_index.remove([fn])
        
    def disk_event_group(events):
        for e in events:
            apply_disk_event_to_filesystem(wd, e, repo=repo)

    fs = {
        DiskEvents.disk_event_group: disk_event_group,
        DiskEvents.dir_create: dir_create,
        DiskEvents.dir_rename: dir_rename,
        DiskEvents.dir_delete: dir_delete,
        DiskEvents.file_create: file_create,
        DiskEvents.file_modify: file_modify,
        DiskEvents.file_delete: file_delete,
        DiskEvents.file_rename: file_rename,
    }
    ename = disk_event['operation']
    if not ename in fs:
        raise NotImplementedError(ename)
    intf = fs[ename]
    arguments = disk_event['arguments']
    try:
#         logger.info('Arguments: %s' % arguments)
        intf(**arguments)
    except Exception as e:
        msg = 'Could not apply this event to filesystem: \n'
        msg += indent(yaml_dump(disk_event), 'disk_event: ')
        msg += '\nwd: %s' % wd
        from mcdp_hdb.memdataview import InvalidOperation
        raise_wrapped(InvalidOperation, e, msg)


