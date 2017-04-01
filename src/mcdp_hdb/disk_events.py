from contracts import contract
from collections import OrderedDict
from decorator import decorator
from mcdp_hdb.disk_struct import ProxyDirectory


class DiskEvents(object):
    dir_create = 'dir_create' # <dirname> <name>
    dir_rename = 'dir_rename' # <dirname> <name> <name2>
    dir_delete = 'dir_delete' # <dirname> <name> 
    file_create = 'file_create' # <dirname> <name> <contents>
    file_modify = 'file_modify' # <dirname> <name> <contents>
    file_delete = 'file_delete' #  <dirname> <name>
    file_rename = 'file_rename' #  <dirname> <name> <basename2>
    
    all_events = [dir_rename, dir_delete, 
                  file_create, file_modify, file_delete, file_rename] 

class DiskView(object):
    @contract(directory=ProxyDirectory)
    def __init__(self, directory):
        self.directory = directory
    
@decorator
def ff(f):
    def f2(_id, who, **args):
        event_name, arguments = f(**args)
        e =  disk_event_make(_id, event_name, who, arguments)
        return e
    return f2

@ff
def disk_event_dir_create(dirname, name):
    return DiskEvents.dir_rename, dict(dirname=dirname, name=name)

def disk_event_dir_create_interpret(view, dirname, name):
    raise NotImplementedError()

@ff
def disk_event_dir_rename(dirname, name, name2):
    return DiskEvents.dir_rename, dict(dirname=dirname, name=name, name2=name2)

def disk_event_dir_rename_interpret(view, dirname, name, name2):
    raise NotImplementedError()

@ff
def disk_event_dir_delete(dirname, name):
    return DiskEvents.dir_delete, dict(dirname=dirname, name=name)

def disk_event_dir_delete_interpret(view, dirname, name):
    raise NotImplementedError()

@ff
def disk_event_file_create(dirname, name, contents):
    return DiskEvents.file_create, dict(dirname=dirname, name=name, contents=contents)

def disk_event_file_create_interpret(view, dirname, name, contents):
    raise NotImplementedError()

@ff
def disk_event_file_modify(dirname, name, contents):
    return DiskEvents.file_modify, dict(dirname=dirname, name=name, contents=contents)

def disk_event_file_modify_interpret(view, dirname, name, contents):
    raise NotImplementedError()

@ff
def disk_event_file_delete(dirname, name):
    return DiskEvents.file_modify, dict(dirname=dirname, name=name)

def disk_event_file_delete_interpret(view, dirname, name):
    raise NotImplementedError()
 
@ff
def disk_event_file_rename(dirname, name, name2):
    return DiskEvents.file_modify, dict(dirname=dirname, name=name, name=name2)

def disk_event_file_rename_interpret(view, dirname, name, name2):
    raise NotImplementedError()



def disk_event_make(_id, event_name, who, arguments):
    assert event_name in DiskEvents.all_events
    d = OrderedDict()
    d['id'] = _id,
    d['operation'] = event_name
    d['who'] = who
    d['arguments']=arguments
    return d

def disk_events_from_memory_events(dm):
    pass