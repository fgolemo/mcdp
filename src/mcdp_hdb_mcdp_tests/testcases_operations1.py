from contracts import contract

from mcdp_hdb_mcdp.main_db_schema import DB
from mcdp_hdb_tests.testcases import get_combinations
from mcdp_hdb_mcdp_tests.dbs import testdb1


@contract(returns='dict(str:isinstance(DataTestCase))')    
def testcases_CommonOperations1():
    
    db_schema = DB.db
    
    db0 = testdb1()

    db_schema.validate(db0)
    
    operation_sequences = []
    def add_seq(f):
        operation_sequences.append(f)
        return f
    
    @add_seq
    def seq_set(view):
        user_db = view.user_db
        user = user_db.users['andrea'] 
        user.info.name = 'new name'
        
    @add_seq
    def seq_append(view):
        user_db = view.user_db
        user = user_db.users['andrea']
        user.info.groups.append('newgroup')
     
    @add_seq
    def seq_delete1(view):
        user_db = view.user_db
        user = user_db.users['andrea']
        user.info.groups.remove('FDM')
   
    disk_maps= {'regular': DB.dm}
    
    prefix = 'commonops1'
    
    res = get_combinations(db_schema, db0, prefix, operation_sequences, disk_maps)
    return res

