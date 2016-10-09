from comptests.registrar import comptest
from mcdp_library import Librarian

from .create_mockups import create_hierarchy


@comptest
def feat_import1():
    """ Poset load """
    data = {
        'lib1.mcdplib/poset1.mcdp_poset': "product(mass:g, energy:J)",
        'lib2.mcdplib/poset2.mcdp_poset': "`lib1.poset1"
    }
    d = create_hierarchy(data)
    librarian = Librarian()
    librarian.find_libraries(d)
    libraries = librarian.get_libraries()
    assert 'lib1' in libraries
    assert 'lib2' in libraries
    assert 'path' in libraries['lib1']
    assert 'library' in libraries['lib1']

    lib1 = librarian.load_library('lib1')
    _poset1 = lib1.load_poset('poset1')
    lib2 = librarian.load_library('lib2')
    _poset2 = lib2.load_poset('poset2')


@comptest
def feat_import2():
    """ NDP load """
    data = {
        'lib1.mcdplib/model1.mcdp': "mcdp {}",
        'lib2.mcdplib/model2.mcdp': "`lib1.model1",
    
        'lib2.mcdplib/model3.mcdp': """\
        mcdp {
            a = new lib1.model1
        }
        """
    }
    d = create_hierarchy(data)
    librarian = Librarian()
    librarian.find_libraries(d)
    lib1 = librarian.load_library('lib1')
    _model1 = lib1.load_ndp('model1')
    lib2 = librarian.load_library('lib2')
    _model2 = lib2.load_ndp('model2')
    _model3 = lib2.load_ndp('model3')

@comptest
def feat_import3():
    """ NDP load """
    data = {
        'lib1.mcdplib/model0.mcdp': "mcdp {}",
        'lib1.mcdplib/model1.mcdp': "`model0",
        'lib2.mcdplib/model2.mcdp': "`lib1.model1",
    }
    d = create_hierarchy(data)
    librarian = Librarian()
    librarian.find_libraries(d)
    lib2 = librarian.load_library('lib2')
    _model2 = lib2.load_ndp('model2')

@comptest
def feat_import4():
    data = {
        'lib1.mcdplib/model0.mcdp': "mcdp {}",
        'lib1.mcdplib/template1.mcdp_template': "template [] mcdp { a = instance `model0 }",
        'lib2.mcdplib/template2.mcdp_template': "`lib1.template1",
        'lib2.mcdplib/model2.mcdp': "specialize [] `template2",
    }
    d = create_hierarchy(data)
    librarian = Librarian()
    librarian.find_libraries(d)
    lib2 = librarian.load_library('lib2')
    _model2 = lib2.load_ndp('model2')

@comptest
def feat_import5():
    pass

@comptest
def feat_import6():
    pass

@comptest
def feat_import7():
    pass

@comptest
def feat_import8():
    pass

@comptest
def feat_import9():
    pass
