from mcdp.constants import MCDPConstants
from mcdp_hdb.schema import SchemaString, Schema
from comptests.registrar import run_module_tests, comptest
from mcdp_shelf.access import ACLRule

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
    authenticated_can_read = ACLRule(ALLOW, MCDPConstants.AUTHENTICATED, READ)
    self_can_modify = ACLRule(ALLOW, 'special:user:$(key:..)', WRITE)

    # admin can read and modify everything
    db_schema.add_acl_rules([admin_can_modify, admin_can_read])
    # all can read the name
    schema_user['name'].add_acl_rules([all_can_read])
    # only authenticated can read the email
    schema_user['email'].add_acl_rules([authenticated_can_read])
    # only the user and admins can modify his entry
    schema_user.add_acl_rules([admin_can_modify, self_can_modify])
    
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


if __name__ == '__main__':
    run_module_tests()