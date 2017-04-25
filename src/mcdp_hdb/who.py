from contracts import new_contract
from contracts.utils import check_isinstance, indent, raise_wrapped

from mcdp_utils_misc.my_yaml import yaml_dump


__all__ = ['assert_valid_who']

@new_contract
def assert_valid_who(who):
    '''
        Raises ValueError if the who is not correct.
        
        who:
            host: <name of host>
            instance: <name of installation>
            actor: <who does the action>
            
        actor can be "system", or "user:*"
    
    '''
    try:
        if not isinstance(who, dict):
            msg = 'who should be a dict'
            raise ValueError(msg)
        
        host = who['host']
        check_isinstance(host, str)
        instance = who['instance']
        check_isinstance(instance, str)
        actor = who['actor']
        check_isinstance(actor, str)
        if actor == 'system':
            # ok
            pass
        elif actor.startswith('user:'):
            # ok
            pass
        else:
            msg = 'Invalid format for actor: %r' % actor
            raise ValueError(msg)
         
    except Exception as e:
        msg = 'Invalid who dictionary:'
        msg += '\n' + indent(yaml_dump(who), '> ')
        raise_wrapped(ValueError, e, msg, compact=True)
        