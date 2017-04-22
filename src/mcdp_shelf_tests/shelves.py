# -*- coding: utf-8 -*-
from nose.tools import assert_equal

from comptests.registrar import comptest, run_module_tests
from mcdp_hdb_mcdp.main_db_schema import DB
from mcdp_tests import logger


# 
# setup_shelve_01 = {
#     'shelf1.' + MCDPConstants.shelf_extension: {
#         MCDPConstants.shelf_desc_file: '''\
# desc_short: shelf 1
# 
# ''',
#         'l1.' +  MCDPConstants.library_extension: {
#             'm1.mcdp': 'mcdp { }',
#         }
#     },
#     'shelf2.'+ MCDPConstants.shelf_extension: {
#         MCDPConstants.shelf_desc_file: '''\
# desc_short: shelf 2
#     
# ''',
#     }
# }
# 
# 
# 
# 
# @comptest
# def shelves01():
#     _d=create_hierarchy(setup_shelve_01)
#     
# setup_permissions = { 
#     'u_andrea_public.' + MCDPConstants.shelf_extension: {
#         MCDPConstants.shelf_desc_file:'''\
#             acl: [
#                 [Allow, Everyone, discover],
#                 [Allow, Everyone, read],
#                 [Allow, user:andrea, write]
#             ]
#         '''
#     },
#     'u_andrea_subscription.' + MCDPConstants.shelf_extension: {
#         MCDPConstants.shelf_desc_file: '''\
#             desc_short: Andrea's subscribers
#             desc_long: 'long desc'
#             dependencies: [u_andrea_public]
#             acl: [
#                 [Allow, Everyone, discover],
#                 [Allow, group:subscribers:andrea, read],
#                 [Allow, user:andrea, read],
#                 [Allow, user:andrea, write],
#                 [Allow, group:admin, discover],
#                 [Allow, group:admin, admin],
#                 [Allow, group:admin, read],
#                 [Allow, group:admin, write]
#             ]
#             authors: [andrea]
#         '''},
#     'u_andrea_private.' + MCDPConstants.shelf_extension: {
#         MCDPConstants.shelf_desc_file: '''\
#             acl: [
#                 [Allow, user:andrea, discover],
#                 [Allow, user:andrea, read],
#                 [Allow, user:andrea, write]
#             ]
#             dependencies: [u_andrea_public]
#             authors: [andrea]
#         '''
#     }
# }
setup_permissions_data = {
    'u_andrea_public': {
        'libraries': {},
        'info': {
            'desc_long': None,
            'desc_short': None,
             'authors': [],
             'dependencies': [],
        },
        'acl': [
            ['Allow', 'Everyone', 'discover'],
            ['Allow', 'Everyone', 'read'],
            ['Allow', 'user:andrea', 'write'],
        ],
    }, 
    'u_andrea_subscription': {
        'libraries': {},
        'acl': [
                ['Allow', 'Everyone', 'discover'],
                ['Allow', 'group:subscribers:andrea', 'read'],
                ['Allow', 'user:andrea', 'read'],
                ['Allow', 'user:andrea', 'write'],
                ['Allow', 'group:admin', 'discover'],
                ['Allow', 'group:admin', 'admin'],
                ['Allow', 'group:admin', 'read'],
                ['Allow', 'group:admin', 'write'],
            ],
        'info': {
            'desc_short': "Andrea's subscribers",
            'desc_long': 'long desc',
            'dependencies': ['u_andrea_public'],
            'authors': ['user:andrea'],
        },
    },
        
    'u_andrea_private': {
        'libraries': {},
        'acl': [
            ['Allow', 'user:andrea', 'discover'],
            ['Allow', 'user:andrea', 'read'],
            ['Allow', 'user:andrea', 'write'],
        ],
        'info': { 
            'desc_long': None,
            'desc_short': None,
            'dependencies': ['u_andrea_public'],
            'authors': ['andrea']
        },
    },
}



@comptest
def shelves02():
    shelves_schema = DB.shelves
    shelves_data = setup_permissions_data
    shelves_schema.validate(shelves_data)
    shelves = DB.view_manager.create_view_instance(shelves_schema, shelves_data)
    shelves.set_root()
    andrea_subscription = shelves['u_andrea_subscription']
    _andrea_private = shelves['u_andrea_private']
    _andrea_public = shelves['u_andrea_public']
    assert len(shelves) == 3, shelves    
    
    print(andrea_subscription)
    acl =  andrea_subscription._get_acl_complete()
    logger.info(acl)
    assert acl.allowed('discover', 'john', groups=[])
    assert  not acl.allowed('read', 'john', groups=[])
    assert acl.allowed('read', 'john', groups=['subscribers:andrea'])
    
    assert_equal(andrea_subscription.get_desc_short(),  "Andrea's subscribers")
    assert_equal(andrea_subscription.get_desc_long(), 'long desc')
    assert_equal(andrea_subscription.get_authors(), ['user:andrea'])
    assert_equal(andrea_subscription.get_dependencies(), ['u_andrea_public'])

    
if __name__ == '__main__':

    run_module_tests()