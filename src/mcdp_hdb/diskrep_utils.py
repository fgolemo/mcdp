from copy import deepcopy
from mcdp_hdb.disk_events import disk_event_interpret
from contracts.utils import indent

def assert_disk_events_consistent(disk_rep0, disk_events, disk_rep1):
    x0 = deepcopy(disk_rep0)
    x = deepcopy(x0)
    for disk_event in disk_events:
        disk_event_interpret(x, disk_event)
    
    assert_diskreps_same(x, disk_rep1, 'obtained', 'disk_rep1')
    
        
def assert_diskreps_same(a, b, a_text='a', b_text='b'):
    n = max(len(a_text), len(b_text))
    a_text = a_text.rjust(n) + ' | '
    b_text = b_text.rjust(n) + ' | '
    
    if a.hash_code() != b.hash_code():
        msg ='The two DiskReps are not the same:'
        msg += '\n' + indent(a.tree(), a_text)
        msg += '\n' +  indent(b.tree(), b_text)
        raise ValueError(msg)
    