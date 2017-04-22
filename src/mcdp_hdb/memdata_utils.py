from copy import deepcopy

from contracts.utils import indent

from mcdp_utils_misc import yaml_dump

from .memdata_events import event_interpret_
from .memdataview_manager import ViewManager

def assert_data_equal(schema, data1, data2):  # @UnusedVariable
    ''' 
        Checks that two datas are the same, by checking the hashcode. 
        Raises ValueError.
    '''
    from .schema import data_hash_code
    
    if data_hash_code(data1) != data_hash_code(data2):
        msg = 'The two datas are different'
        msg += '\n'
        msg += indent(yaml_dump(data1), ' data1 ')
        msg += '\n'
        msg += indent(yaml_dump(data2), ' data2 ')
        raise ValueError(msg)
    
def assert_data_events_consistent(schema, data1, events, data2):
    from .schema import data_hash_code
    h = data_hash_code(data1)    
    view_manager = ViewManager(schema)
    # verify consistency
    data_i = deepcopy(data1)
    for event in events:
        view = view_manager.view(data_i)
        event_interpret_(view, event)
    
    # check we didn't change data1 at all
    h2 = data_hash_code(data1)
    assert h == h2    
        
    assert_data_equal(schema, data2, data_i)
