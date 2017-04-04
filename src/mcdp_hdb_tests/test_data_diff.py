from comptests.registrar import run_module_tests, comptest
from mcdp_hdb.schema import SchemaContext, SchemaList, SchemaHash, SchemaString
from mcdp_hdb.memdata_diff import data_diff
from mcdp_hdb.memdata_utils import assert_data_events_consistent


@comptest
def test_data_diff_basic1():
    schema = SchemaContext()
    schema.string('name')
    d1 = {'name': 'bob'}
    d2 = {'name': 'bill'}
    check_data_diff(schema, d1, d2)

@comptest
def test_data_diff_basic1_hash():
    user = SchemaContext()
    user.string('name')
    d1 = {'user1': {'name': 'bob'}}
    d2 = {'user1': {'name': 'bill'}}
    
    schema = SchemaHash(user)
    check_data_diff(schema, d1, d2)

@comptest
def test_data_diff_basic_list1_append():
    schema = SchemaList(SchemaString())
    d1 = ['a']
    d2 = ['a','b']
    check_data_diff(schema, d1, d2)

@comptest
def test_data_diff_basic_list1_remove1():
    schema = SchemaList(SchemaString())
    d1 = ['a', 'b']
    d2 = ['b']
    check_data_diff(schema, d1, d2)

@comptest
def test_data_diff_basic_list1_remove2():
    schema = SchemaList(SchemaString())
    d1 = ['a', 'b']
    d2 = ['b']
    check_data_diff(schema, d1, d2)

@comptest
def test_data_diff_basic_list2():
    user = SchemaContext()
    user.string('name')
    schema = SchemaList(user)
    d1 = [
        {'name': 'bob'},
    ]
    d2 = [
        {'name': 'bill'},
    ]
    check_data_diff(schema, d1, d2)
    
def check_data_diff(schema, d1, d2):
    schema.validate(d1)
    schema.validate(d2)
    events = data_diff(schema, d1, d2)
    assert_data_events_consistent(schema, d1, events, d2)
    
    events_inv = data_diff(schema, d2, d1)
    assert_data_events_consistent(schema, d2, events_inv, d1)
    
if __name__ == '__main__':
    run_module_tests()
