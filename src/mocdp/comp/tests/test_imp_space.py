from comptests.registrar import comptest
from mcdp_dp.dp_transformations import get_dp_bounds
from mcdp_dp.primitive import NotSolvableNeedsApprox
from mcdp_lang.parse_interface import parse_ndp
from mcdp_posets.space_product import SpaceProduct
from mcdp_tests.generation import for_all_nameddps
from mocdp import ATTRIBUTE_NDP_RECURSIVE_NAME
from mocdp.comp.composite import CompositeNamedDP
from mocdp.comp.composite_makecanonical import cndp_makecanonical
from mocdp.comp.recursive_name_labeling import (get_imp_as_recursive_dict,
    get_names_used, label_with_recursive_names, ndp_make)


# mocdp.comp.test.tests.test_imp_space.make_one
def make_root(ndp, res, context):  # @UnusedVariable
    print('make_root(%s)' % res)
    assert res['a']['status'] == 'make_a_ok'
    assert res['b']['status'] == 'make_b_ok'
    bom = set(res['a']['bom'] + res['b']['bom'])
    return {'bom': bom, 'status': 'make_root_ok'}

def make_a(ndp, res, context):  # @UnusedVariable
    print('make_a(%r)' % res)
    assert res['a2']['status'] == 'make_a2_ok'

    return {'bom': res['a2']['bom'], 'status': 'make_a_ok'}

def make_b(ndp, res, context):  # @UnusedVariable
    assert res in ['model3', 'model4']
    return {'bom': [res], 'status': 'make_b_ok'}

def make_a2(ndp, res, context):  # @UnusedVariable
    assert res in ['model1', 'model2']
    return {'bom': [res], 'status': 'make_a2_ok'}

@comptest
def test_imp_space_2():
    ndp0 = parse_ndp("""
addmake(code mocdp.comp.tests.test_imp_space.make_root)
mcdp {
    a = instance 
        addmake(code mocdp.comp.tests.test_imp_space.make_a)
        mcdp {
        
        a2 = instance 
        
        addmake(code mocdp.comp.tests.test_imp_space.make_a2) 
        catalogue {
            provides capacity [J]
            requires mass [g]
            
            model1 | 1 J | 200 g
            model2 | 2 J | 300 g
        }
        
        provides capacity using a2
        requires mass >= 10g + a2.mass 
    }
    
    b = instance 
    addmake(code mocdp.comp.tests.test_imp_space.make_b)
    catalogue {
        provides capacity [J]
        requires mass [g]
        
        model3 | 1 J | 200 g
        model4 | 2 J | 300 g
    }
    
    provides capacity <= a.capacity + b.capacity
    requires mass >= a.mass + b.mass
}

    """)
    assert isinstance(ndp0, CompositeNamedDP)
    label_with_recursive_names(ndp0)
    ndp = cndp_makecanonical(ndp0)
    dp0 = ndp.get_dp()
    print dp0.repr_long()
    dp, _ = get_dp_bounds(dp0, 5, 5)
    f = 0.0
    R = dp.get_res_space()
    ur = dp.solve(f)
    I = dp.get_imp_space()
    assert isinstance(I, SpaceProduct)

    print('I: %s' % I)
    print('get_names_used: %s' % get_names_used(I))

    for r in ur.minimals:
        print('r = %s' % R.format(r))
        imps = dp.get_implementations_f_r(f, r)
        print('imps: %s' % imps)

        for imp in imps:
            I.belongs(imp)
            imp_dict = get_imp_as_recursive_dict(I, imp)  # , ignore_hidden=False)
            print('imp dict: %r' % imp_dict)
            assert set(imp_dict) == set(['a', 'b', '_sum1', '_invplus1', 'capacity', 'mass']), imp_dict
            assert set(imp_dict['a']) == set(['_plus1', 'a2', ]), imp_dict['a']
            context = {}
            artifact = ndp_make(ndp0, imp_dict, context)
            print('artifact: %s' % artifact)


@for_all_nameddps
def test_imp_dict_1(id_ndp, ndp):
    if '_inf' in id_ndp:  # infinite
        return
    label_with_recursive_names(ndp)
    dp0 = ndp.get_dp()
    F = dp0.get_fun_space()
    I = dp0.get_imp_space()
    print ndp.repr_long()
    print dp0.repr_long()
    print('I: %s' % I)
#     print('get_names_used: %s' % get_names_used(I))

    f = list(F.get_minimal_elements())[0]
    try:
        ur = dp0.solve(f)
    except NotSolvableNeedsApprox:
        return

    for r in ur.minimals:
        imps = dp0.get_implementations_f_r(f, r)
        for imp in imps:
            I.belongs(imp)
            context = {}
            imp_dict = get_imp_as_recursive_dict(I, imp)
            artifact = ndp_make(ndp, imp_dict, context)
            print('artifact: %s' % artifact.__repr__())
            

@for_all_nameddps
def test_imp_dict_2_makecanonical(id_ndp, ndp0):
    """ This one also canonicalizes. """
    if '_inf' in id_ndp:  # infinite
        return

    if not isinstance(ndp0, CompositeNamedDP):
        print('skipping because not CompositeNamedDP: %s' % type(ndp0).__name__)
        return
    label_with_recursive_names(ndp0)
    ndp = cndp_makecanonical(ndp0)
    dp0 = ndp.get_dp()
    F = dp0.get_fun_space()
    I = dp0.get_imp_space()
    assert isinstance(I, SpaceProduct)
    print ndp.repr_long()
    print('I: %s' % I)
    print('get_names_used: %s' % get_names_used(I))

    f = list(F.get_minimal_elements())[0]

    try:
        ur = dp0.solve(f)
    except NotSolvableNeedsApprox:
        return

    for r in ur.minimals:
        imps = dp0.get_implementations_f_r(f, r)
        for imp in imps:
            I.belongs(imp)
            context = {}
            imp_dict = get_imp_as_recursive_dict(I, imp)
            artifact = ndp_make(ndp0, imp_dict, context)
            print('artifact: %s' % artifact)


@comptest
def test_imp_space_3():
    pass

@comptest
def test_imp_space_4():
    pass

@comptest
def test_imp_space_5():
    pass

@comptest
def test_imp_space_6():
    pass

@comptest
def test_imp_space_7():
    pass

@comptest
def test_imp_space_8():
    pass



@comptest
def test_imp_space_1():
    ndp0 = parse_ndp("""
mcdp {
    actuation = instance mcdp {
        # actuators need to provide this lift
        provides lift [N]
        # and will require power
        requires power [W]
        # simple model: quadratic
        c = 0.002 W/N^2
        power >= lift * lift * c
        
        a = instance catalogue {
            provides a [N]
            one  |10N
        }
        a.a >= 0N
    }
    
    requires power for actuation
    provides lift using actuation
}

    """)
    assert isinstance(ndp0, CompositeNamedDP)
    label_with_recursive_names(ndp0)
#     ndp = cndp_makecanonical(ndp0)
    ndp = ndp0
    dp = ndp.get_dp()
    print ndp.repr_long()
    print dp.repr_long()
    f = 0.0
    R = dp.get_res_space()
    ur = dp.solve(f)
    I = dp.get_imp_space()
    assert isinstance(I, SpaceProduct)
    print(getattr(I, ATTRIBUTE_NDP_RECURSIVE_NAME, 'no attr'))
    print('I: %s' % I)
    print('get_names_used: %s' % get_names_used(I))

    for r in ur.minimals:
        print('r = %s' % R.format(r))
        imps = dp.get_implementations_f_r(f, r)
        print('imps: %s' % imps)

        for imp in imps:
            I.belongs(imp)
            imp_dict = get_imp_as_recursive_dict(I, imp)
            print('imp dict: %r' % imp_dict)
            assert set(imp_dict) == set(['power', 'lift', 'actuation']), imp_dict
            assert set(imp_dict['actuation']) == \
                set(['_mult1', 'a', 'power', '_c1', '_prod1', 'lift']), imp_dict['actuation']

            context = {}
            artifact = ndp_make(ndp0, imp_dict, context)
            print('artifact: %s' % artifact)
