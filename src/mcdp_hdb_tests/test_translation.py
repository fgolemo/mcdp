# -*- coding: utf-8 -*-
from copy import deepcopy

from contracts.utils import indent
from nose.tools import assert_equal
import yaml

from comptests.registrar import comptest, run_module_tests
from mcdp.logs import logger
from mcdp_hdb.schema import Schema, SchemaString
from mcdp_hdb.dbview import ViewManager
from mcdp_hdb.change_events import replay_events 

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
    db = deepcopy(db0)
    events = []
    viewmanager = ViewManager(db_schema) 
    view = viewmanager.view(db)
    def notify_callback(event):
        logger.debug('\n' + yaml.dump(event))
        events.append(event)
    view._notify_callback = notify_callback

    users = view.users
    u = users['andrea'] 
    u.name = 'not Andrea'
    u.email = None    
    users['another'] = {'name': 'Another', 'email': 'another@email.com', 'groups':[]}
    del users['another']
    users.rename('pinco', 'pallo')
    db2 = replay_events(viewmanager, db0, events) 
    assert_equal(db, db2)
    
if __name__ == '__main__':
    run_module_tests()