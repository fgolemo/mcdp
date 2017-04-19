from mcdp.constants import MCDPConstants
from mcdp_hdb.schema import SchemaString, Schema
from comptests.registrar import run_module_tests, comptest
from mcdp_shelf.access import ACLRule
from mcdp_hdb import InsufficientPrivileges, ViewManager
from contextlib import contextmanager

@comptest
def test_privilege1():
    # define schema
    db_schema = Schema()
    schema_user = Schema()
    schema_user.string('name')
    schema_user.string('email', can_be_none=True)
    schema_user.list('groups', SchemaString())
    db_schema.hash('users', schema_user)
    
    ALLOW = MCDPConstants.ALLOW
    READ = MCDPConstants.Privileges.READ
    WRITE = MCDPConstants.Privileges.WRITE
    # give access control
    admin_can_read = ACLRule(ALLOW, 'group:admin', READ)
    admin_can_modify = ACLRule(ALLOW, 'group:admin', WRITE)
    all_can_read = ACLRule(ALLOW, MCDPConstants.EVERYONE, READ)
    #authenticated_can_read = ACLRule(ALLOW, MCDPConstants.AUTHENTICATED, READ)
    self_can_modify = ACLRule(ALLOW, 'special:user:${path[-2]}', WRITE)
    self_can_read = ACLRule(ALLOW, 'special:user:${path[-2]}', READ)

    # admin can read and modify everything
    db_schema.add_acl_rules([admin_can_modify, admin_can_read])
    # all can read the name
    schema_user['name'].add_acl_rules([all_can_read])
    # only the user itself can read the email
    # schema_user['email'].add_acl_rules([authenticated_can_read])
    # only the user and admins can modify his entry
    schema_user.add_acl_rules([admin_can_modify, admin_can_read, self_can_modify, self_can_read])
    
    print db_schema
    db0 = {
        'users': { 
            'andrea': {
                'name': 'Andrea', 
                'email': 'info@co-design.science',
                'groups': ['group:admin', 'group:FDM'],
            },
            'pinco': {
                'name': 'Pinco Pallo', 
                'email': None,
                'groups': ['group:FDM'],
            },
        }
    }
    EVERYONE = MCDPConstants.EVERYONE
    AUTHENTICATED = MCDPConstants.AUTHENTICATED
    view_manager = ViewManager(db_schema)
    view_andrea = view_manager.view(db0, 'user:andrea', ['user:andrea', AUTHENTICATED, EVERYONE])
    view_pinco = view_manager.view(db0, 'user:pinco', ['user:pinco', AUTHENTICATED, EVERYONE])
    view_admin = view_manager.view(db0, 'user:admin1', ['user:admin1', 'group:admin', AUTHENTICATED, EVERYONE])

    # andrea is able to read his email
    print('andrea can see ' + view_andrea.child('users').child('andrea').email)
    # pinco can read andrea's name
    view_pinco.child('users').child('andrea').name
    # pinco cannot read andrea's email
    with expect_permissions_error():
        print('! pinco can see ' + view_pinco.child('users').child('andrea').email)
    # pinco cannot change andrea's name
    with expect_permissions_error():
        view_pinco.child('users').child('andrea').name = 'invalid'
    # admin can change andrea's name
    view_admin.child('users').child('andrea').name = 'xxx'
    # andrea can change andrea's name
    view_andrea.child('users').child('andrea').name = 'xxx'
    
@contextmanager
def expect_permissions_error():
    try:
        yield
    except InsufficientPrivileges:
        pass
    else:
        msg = 'Expected InsufficientPrivileges'
        raise Exception(msg)

if __name__ == '__main__':
    run_module_tests()
    
    