from collections import OrderedDict
from copy import deepcopy
import os
import shutil

from contracts import contract, new_contract
from contracts.utils import check_isinstance, indent, raise_wrapped

from mcdp.logs import logger
from mcdp_utils_misc import yaml_dump

from .disk_struct import ProxyDirectory, ProxyFile
from .disk_errors import InvalidDiskOperation


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
    @contract(_id=str)
    def f2(_id, who, *args, **kwargs):
        check_isinstance(_id, str)
        logger.debug('Calling %s with args = %s kwargs = %s' % (f, args, kwargs))
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
        raise InvalidDiskOperation(msg)
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

def apply_disk_event_to_filesystem(wd, disk_event): 
    
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
        
    def file_rename(dirname, name, name2):
        p1 = as_path(dirname, name)
        p2 = as_path(dirname, name2)
        os.rename(p1, p2)
        
    def dir_delete(dirname, name):
        p = as_path(dirname, name)
        shutil.rmtree(p) 
        
    def file_create(dirname, name, contents):
        p = as_path(dirname, name)
        with open(p, 'wb') as f:
            f.write(contents)
    
    def file_modify(dirname, name, contents):
        p = as_path(dirname, name)
        with open(p, 'wb') as f:
            f.write(contents)
    
    def file_delete(dirname, name):
        p = as_path(dirname, name)
        os.unlink(p)
        
    def disk_event_group(events):
        for e in events:
            apply_disk_event_to_filesystem(wd, e)

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
        logger.info('Arguments: %s' % arguments)
        intf(**arguments)
    except Exception as e:
        msg = 'Could not apply this event to filesystem: \n'
        msg += indent(yaml_dump(disk_event), 'disk_event: ')
        from mcdp_hdb.memdataview import InvalidOperation
        raise_wrapped(InvalidOperation, e, msg)


