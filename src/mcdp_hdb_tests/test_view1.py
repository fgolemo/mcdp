# -*- coding: utf-8 -*-
from copy import deepcopy

from contracts.utils import indent
from nose.tools import assert_equal

from comptests.registrar import comptest, run_module_tests
from mcdp import MCDPConstants
from mcdp.logs import logger
from mcdp_hdb import Schema, NotValid, SchemaString
from mcdp_hdb import ViewManager
from mcdp_hdb import replay_events
from mcdp_shelf import ACLRule
from mcdp_utils_misc import yaml_dump


def l(what, s):
    logger.info('\n' + indent(s, '%010s │  ' % what))

@comptest
def test_view1a():
    
    db_schema = Schema()
    schema_user = Schema()
    schema_user.string('name')
    schema_user.string('email', can_be_none=True)
    schema_user.list('groups', SchemaString())
    db_schema.hash('users', schema_user)
    
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

    db_schema.validate(db0)
    all_everything = ACLRule(MCDPConstants.ALLOW, 
                             MCDPConstants.EVERYONE, 
                             MCDPConstants.Privileges.SPECIAL_ALL_WILDCARD)
    db_schema.add_acl_rules([all_everything])
    db = deepcopy(db0)
    
    class UserView():
        def get_complete_address(self):
            return '%s <%s>' %  (self.name, self.email)
    
    viewmanager = ViewManager(db_schema)
    viewmanager.set_view_class(schema_user, UserView) 
    actor = 'user:andrea'
    principals = ['user:andrea', MCDPConstants.EVERYONE]
    view = viewmanager.view(db, actor, principals)
    events = []
    def notify_callback(event):
        logger.debug('\n' + yaml_dump(event))
        events.append(event)
    view._notify_callback = notify_callback
    users = view.users
    
    u = users['andrea'] 
    assert_equal(u.name, 'Andrea')
    u.name = 'not Andrea'
    assert_equal(u.name, 'not Andrea')
    assert_equal(u.get_complete_address(), 'not Andrea <info@co-design.science>')
    try:
        u.email = None
    except:
        raise Exception('Should have been fine')
    
    assert_equal(u.email, None)
    
    try:
        u.name = None
    except NotValid as e:
        logger.info(e)
    else:
        raise Exception('Name set to None')
    
    assert u._data['name'] is not None, u._data
    
    users['another'] = {'name': 'Another', 'email': 'another@email.com', 'groups':[]}
    
    # no email

    try:
        users['another'] = {'name': 'Another'}
        raise Exception('Expected NotValid')
    except NotValid:
        pass

    assert 'another' in users
    del users['another']
    assert 'another' not in users

    for group in u.groups:
        print('%s is in group %s' % (u.name, group))
    
    assert_equal(list(u.groups), ['group:admin', 'group:FDM'])
    
    users.rename('pinco', 'pallo')
    all_users = set(users)
    print all_users
    assert_equal(all_users, set(['pallo','andrea']))

    l('db', yaml_dump(db))
     
    print yaml_dump(events)
    db2 = replay_events(viewmanager, db0, events) 
    
    l('db2', yaml_dump(db2))
    assert_equal(db, db2)
    
if __name__ == '__main__':
    run_module_tests()
    
    