from contracts.utils import indent
import yaml
from contracts.utils import raise_wrapped
from mcdp.logs import logger

def event_set(_id, who, what, value):
    event = {
     'operation': 'set', 
     'id': _id,
     'who': who, 
     'arguments': {
         'what': list(what), 
         'value': value,
        }
    }
    return event

def event_delete(_id, who, what):
    event = {
     'operation': 'delete', 
     'id': _id,
     'who': who, 
     'arguments': {
         'what': list(what),
        }
    }
    return event

def event_rename(_id, who, what, key2):
    event = {
     'operation': 'rename', 
     'id': _id,
     'who': who, 
     'arguments': {
         'what': list(what),
         'value': key2,
        }
    }
    return event

def replay_events(view_manager, db0, events):
    from mcdp_hdb_tests.dbview import InvalidOperation, ViewHash0

    v0 = view_manager.view(db0, who={})
    def get(w):
        v = v0
        while len(w):
            v = v.child(w[0])
            w = w[1:]
        return v
    
    for event in events:
        try:
            args = event['arguments']
            if event['operation'] == 'set':
                what = tuple(args['what'])
                value = args['value']
                if len(what) > 1: # maybe >= 1
                    prev = get(what[:-1])
                    if isinstance(prev, ViewHash0):
                        key = what[-1]
                        prev[key] = value
                    else:
                        v = get(what)
                        v.set(value)
                else:
                    v = get(what)
                    v._schema.validate(value)
                    v.set(value)
            elif event['operation'] == 'delete':
                what = tuple(args['what'])
                assert len(what) >= 1
                
                prev = get(what[:-1])
                if isinstance(prev, ViewHash0):
                    key = what[-1]
                    del prev[key]
                else:
                    msg = 'Not implemented with %s' % prev
                    raise InvalidOperation(msg)
            elif event['operation'] == 'rename':
                what = tuple(args['what'])
                assert len(what) >= 1
                
                prev = get(what[:-1])
                if isinstance(prev, ViewHash0):
                    key = what[-1]
                    key2 = args['value']
                    prev.rename(key, key2)
                else:
                    msg = 'Not implemented with %s' % prev
                    raise InvalidOperation(msg)
            else:
                raise InvalidOperation(event['operation'])
        except Exception as e:
            msg = 'Could not complete the replay of this event: \n'
            msg += indent(yaml.dump(event), 'event: ')
            raise_wrapped(InvalidOperation, e, msg)
            
        msg = '\nAfter playing event:\n'
        msg += indent(yaml.dump(event), '   event: ')
        msg += '\nthe DB is:\n'
        msg += indent(yaml.dump(db0), '   db: ')
        logger.debug(msg)
        
        v0._schema.validate(db0)
    return db0