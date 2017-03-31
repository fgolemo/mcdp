# -*- coding: utf-8 -*-
from contracts.utils import indent
from nose.tools import assert_equal

from comptests.registrar import comptest, run_module_tests
from mcdp.logs import logger
from mcdp_hdb.schema import Schema, NotValid, SchemaString
from mcdp_hdb_tests.dbview import ViewManager
import yaml


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
    
    db = {
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

    db_schema.validate(db)
    
    class UserView():
        def get_complete_address(self):
            return '%s <%s>' %  (self.name, self.email)
    
    viewmanager = ViewManager(db_schema)
    viewmanager.set_view_class(schema_user, UserView) 
                              
    view = viewmanager.view(db)
    
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
        raise Exception('Name set to None')
    except:
        pass
    
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

    l('db', yaml.dump(db))
    
#     
#     
#     
#     
#     image = Schema()
#     for ext in exts:
#         image.bytes(ext, can_be_none=True) # and can be none
#     s.hash('images', image)
#     
#     l('schema', s)
# 
#     dm = DiskMap()
#     dm.hint_extensions(s['images'], exts)
# 
# #     data = s.generate()
#     
#     d = 'contents'
#     h0 = {'images': {'im1.jpg': d, 'im2.png': d, 'im2.jpg': d}}
#     l('h0', yaml.dump(h0))
#     
#     data = dm.interpret_hierarchy(s, h0)
#     l('data', yaml.dump(data))
#     s.validate(data)
# #     
# #     dm1 = DiskMap()
# #     h1 = dm1.create_hierarchy(s, data)
# #     l('h1', yaml.dump(h1))
# 
#     h1 = dm.create_hierarchy(s, data)
#     l('h1', yaml.dump(h1))


if __name__ == '__main__':
    run_module_tests()