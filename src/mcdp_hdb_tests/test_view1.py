# -*- coding: utf-8 -*-
from mcdp_hdb.schema import Schema
from comptests.registrar import comptest, run_module_tests
from mcdp.constants import MCDPConstants
import yaml
from mcdp.logs import logger
from contracts.utils import indent
from mcdp_hdb.disk_map import DiskMap
from mcdp_hdb_tests.dbview import ViewManager
from nose.tools import assert_equal

def l(what, s):
    logger.info('\n' + indent(s, '%010s │  ' % what))

@comptest
def test_view1a():
    
    db_schema = Schema()
    schema_user = Schema()
    schema_user.string('name')
    schema_user.string('email', can_be_none=True)
    db_schema.hash('users', schema_user)
    
    db = {'users': 
          { 'andrea': {'name': 'Andrea', 'email': 'info@co-design.science'},
                    'pinco': {'name': 'Pinco Pallo', 'email': None}}}
    
    db_schema.validate(db)
    
    class UserView():
        def get_complete_address(self):
            return '%s <%s>' %  (self.name, self.email)
    
    viewmanager = ViewManager(db_schema)
    viewmanager.set_view_class(schema_user, UserView) 
                              
    view = viewmanager.view(db)
    
    u = view.users['andrea'] 
    assert_equal(u.name, 'Andrea')
    u.name = 'not Andrea'
    assert_equal(u.name, 'not Andrea')
    assert_equal(u.get_complete_address(), 'not Andrea <info@co-design.science>')
    try:
        # Violates contract
        u.email = None
    except:
        pass
    
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