from contracts import contract

from mcdp_hdb_mcdp.main_db_schema import DB
from mcdp_hdb_tests.testcases import get_combinations


@contract(returns='dict(str:isinstance(DataTestCase))')    
def testcases_CommonOperations1():
    
    db_schema = DB.db
    
    db0 = {
        'repos': {},
        'user_db' : {
            'users': {
                'andrea': {
                    'name': 'Andrea',
                    'groups': ['one', 'two'],
                }
            }
        }
    }

    db_schema.validate(db0)
    
    operation_sequences = []
    def add_seq(f):
        operation_sequences.append(f)
        return f
    
    @add_seq
    def seq_set(view):
        user_db = view.user_db
        user_db.users['andrea'].name = 'new name'
        
    @add_seq
    def seq_append(view):
        user_db = view.user_db
        user_db.users['andrea'].groups.append('newgroup')
     
    @add_seq
    def seq_delete1(view):
        user_db = view.user_db
        user_db.users['andrea'].groups.remove('one')
   
    disk_maps= {'regular': DB.dm}
    
    prefix = 'array_inside_yaml'
    
    res = get_combinations(db_schema, db0, prefix, operation_sequences, disk_maps)
    return res

