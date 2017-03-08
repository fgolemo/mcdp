# -*- coding: utf-8 -*-
from comptests.registrar import comptest, run_module_tests
from mcdp_library_tests.create_mockups import create_hierarchy
from mcdp_shelf.shelves import find_shelves
from nose.tools import assert_equal
from mcdp.constants import MCDPConstants


setup_shelve_01 = {
    'shelf1.' + MCDPConstants.shelf_extension: {
        MCDPConstants.shelf_desc_file: '''\
name: shelf 1
access: {}
''',
        'l1.' +  MCDPConstants.library_extension: {
            'm1.mcdp': 'mcdp { }',
        }
    },
    'shelf2.'+ MCDPConstants.shelf_extension: {
        MCDPConstants.shelf_desc_file: '''\
name: shelf 2
access: {}
    
''',
    }
}




@comptest
def shelves01():
    _d=create_hierarchy(setup_shelve_01)
    
setup_permissions = { 
    'u_andrea_public.' + MCDPConstants.shelf_extension: {
        MCDPConstants.shelf_desc_file:'''\
            acl: [
                [Allow, Everyone, discover],
                [Allow, Everyone, read],
                [Allow, andrea, write]
            ]
        '''
    },
    'u_andrea_subscription.' + MCDPConstants.shelf_extension: {
        MCDPConstants.shelf_desc_file: '''\
            desc_short: Andrea's subscribers
            desc_long: 'long desc'
            dependencies: [u_andrea_public]
            acl: [
                [Allow, Everyone, discover],
                [Allow, "groups:subscribers:andrea", read],
                [Allow, andrea, read],
                [Allow, andrea, write],
                [Allow, "groups:admin", discover],
                [Allow, "groups:admin", admin],
                [Allow, "groups:admin", read],
                [Allow, "groups:admin", write]
            ]
            authors: [andrea]
        '''},
    'u_andrea_private.' + MCDPConstants.shelf_extension: {
        MCDPConstants.shelf_desc_file: '''\
            acl: [
                [Allow, andrea, discover],
                [Allow, andrea, read],
                [Allow, andrea, write]
            ]
            dependencies: [u_andrea_public]
            authors: [andrea]
        '''
    }
}


@comptest
def shelves02():
    d = create_hierarchy(setup_permissions)
    
    shelves = find_shelves(d)
    andrea_subscription = shelves['u_andrea_subscription']
    _andrea_private = shelves['u_andrea_private']
    _andrea_public = shelves['u_andrea_public']
    assert len(shelves) == 3, shelves    
    
    assert andrea_subscription.get_acl().allowed('discover', 'john', groups=[])
    assert not andrea_subscription.get_acl().allowed('read', 'john', groups=[])
    assert andrea_subscription.get_acl().allowed('read', 'john', groups=['subscribers:andrea'])
    
    assert_equal(andrea_subscription.get_desc_short(),  "Andrea's subscribers")
    assert_equal(andrea_subscription.get_desc_long(), 'long desc')
    assert_equal(andrea_subscription.get_authors(), ['andrea'])
    assert_equal(andrea_subscription.get_dependencies(), ['u_andrea_public'])

    
if __name__ == '__main__':

    run_module_tests()