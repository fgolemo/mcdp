from collections import OrderedDict

from contracts import contract
from contracts.utils import check_isinstance, indent, raise_wrapped

from mcdp.logs import logger
from mcdp_utils_misc import format_list, yaml_dump

from .disk_struct import ProxyDirectory, ProxyFile
from mcdp_hdb.disk_errors import InvalidDiskOperation



class DiskEvents(object):
    dir_create = 'dir_create' # <dirname> <name>
    dir_rename = 'dir_rename' # <dirname> <name> <name2>
    dir_delete = 'dir_delete' # <dirname> <name> 
    file_create = 'file_create' # <dirname> <name> <contents>
    file_modify = 'file_modify' # <dirname> <name> <contents>
    file_delete = 'file_delete' #  <dirname> <name>
    file_rename = 'file_rename' #  <dirname> <name> <basename2>
    
    all_events = [dir_rename, dir_delete, dir_create,
                  file_create, file_modify, file_delete, file_rename] 

class DirView(object):

    @contract(directory=ProxyDirectory)
    def __init__(self, directory):
        self.directory = directory

class DiskView(DirView):
    
    def __init__(self, directory):
        DirView.__init__(self, directory)
        self._event_callback = None

    
# @decorator
def ff(f):
    @contract(_id=str)
    def f2(_id, who, *args, **kwargs):
        check_isinstance(_id, str)
        logger.debug('Calling %s with args = %s kwargs = %s' % (f, args, kwargs))
        event_name, arguments = f(*args, **kwargs)
        e =  disk_event_make(_id, event_name, who, arguments)
        return e
    return f2

@ff
def disk_event_dir_create(dirname, name):
    return DiskEvents.dir_create, dict(dirname=dirname, name=name)

def disk_event_dir_create_interpret(disk_rep, dirname, name):
    d = disk_rep.get_descendant(dirname)
    d[name] = ProxyDirectory()

@ff
def disk_event_dir_rename(dirname, name, name2):
    return DiskEvents.dir_rename, dict(dirname=dirname, name=name, name2=name2)

def disk_event_dir_rename_interpret(disk_rep, dirname, name, name2):
    d = disk_rep.get_descendant(dirname)
    
    d.dir_rename(name, name2)


@ff
def disk_event_dir_delete(dirname, name):
    return DiskEvents.dir_delete, dict(dirname=dirname, name=name)

def disk_event_dir_delete_interpret(disk_rep, dirname, name):
    d = disk_rep.get_descendant(dirname)
    d.dir_delete(name)


@ff
def disk_event_file_create(dirname, name, contents):
    return DiskEvents.file_create, dict(dirname=dirname, name=name, contents=contents)

def disk_event_file_create_interpret(disk_rep, dirname, name, contents):
    d = disk_rep.get_descendant(dirname)
    d.file_create(name, contents)

@ff
def disk_event_file_modify(dirname, name, contents):
    return DiskEvents.file_modify, dict(dirname=dirname, name=name, contents=contents)

def disk_event_file_modify_interpret(disk_rep, dirname, name, contents):
    d = disk_rep.get_descendant(dirname)
    d.file_modify(name, contents)

@ff
def disk_event_file_delete(dirname, name):
    return DiskEvents.file_delete, dict(dirname=dirname, name=name)

def disk_event_file_delete_interpret(disk_rep, dirname, name):
    d = disk_rep.get_descendant(dirname)
    d.file_delete(name)
 
@ff
def disk_event_file_rename(dirname, name, name2):
    return DiskEvents.file_rename, dict(dirname=dirname, name=name, name2=name2)

def disk_event_file_rename_interpret(disk_rep, dirname, name, name2):
    raise NotImplementedError()

def disk_event_make(_id, event_name, who, arguments):
    assert event_name in DiskEvents.all_events, event_name
    d = OrderedDict()
    d['id'] = _id
    d['operation'] = event_name
    d['who'] = who
    d['arguments']=arguments
    return d

#     dir_create = 'dir_create' # <dirname> <name>
#     dir_rename = 'dir_rename' # <dirname> <name> <name2>
#     dir_delete = 'dir_delete' # <dirname> <name> 
#     file_create = 'file_create' # <dirname> <name> <contents>
#     file_modify = 'file_modify' # <dirname> <name> <contents>
#     file_delete = 'file_delete' #  <dirname> <name>
#     file_rename = 'file_rename' #  <dirname> <name> <basename2>
#     

@contract(disk_rep=ProxyDirectory)
def disk_event_interpret(disk_rep, disk_event):
    fs = {
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
        logger.info('Arguments: %s' % arguments)
        intf(disk_rep=disk_rep, **arguments)
    except Exception as e:
        msg = 'Could not complete the replay of this event: \n'
        msg += indent(yaml_dump(disk_event), 'disk_event: ')
        msg += '\nFor this tree:\n'
        msg += indent((disk_rep.tree()), ' disk_rep: ')
        from mcdp_hdb.dbview import InvalidOperation
        raise_wrapped(InvalidOperation, e, msg)
