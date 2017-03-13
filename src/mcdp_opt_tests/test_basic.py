# -*- coding: utf-8 -*-
import os
import shutil

from comptests.registrar import comptest, comptest_fails
from contracts import contract
from mcdp_lang import parse_constant, parse_poset
from mcdp_library import Librarian, MCDPLibrary
from mcdp_opt.compare_different_resources import less_resources2
from mcdp_opt.optimization import Optimization
from mcdp_posets import Nat, Poset, PosetProduct, UpperSet
from mcdp_posets.types_universe import express_value_in_isomorphic_space
from mcdp_report.gdc import STYLE_GREENREDSYM
from mcdp_report.gg_ndp import gvgen_from_ndp
from mcdp_report.gg_utils import gg_figure
from mocdp.comp.composite import cndp_get_name_ndp_notfunres
from mocdp.comp.composite_templatize import cndp_templatize_children
from mcdp.exceptions import mcdp_dev_warning
from reprep import Report
from mcdp.constants import MCDPConstants
from mcdp_utils_misc.dir_from_package_nam import dir_from_package_name
from mcdp_library.specs_def import SPEC_MODELS


def get_test_library2(libnames):
    package = dir_from_package_name('mcdp_data')
    all_libraries = os.path.join(package, 'libraries')

    librarian = Librarian()
    librarian.find_libraries(all_libraries)

    l = MCDPLibrary()
    for lib in libnames:
        data = librarian.libraries[lib]
        path = data['path']
        l.add_search_dir(path)

    l.load_library_hooks.append(librarian.load_library)
    return l

# @comptest
def opt_basic_1_long():
    libnames = ['actuation']
    library = get_test_library2(libnames)
    
    outdir = 'out/opt_basic_1'
    
    library.use_cache_dir(os.path.join(outdir, 'cache'))

    options = library.list_spec(SPEC_MODELS)
    options.remove('RigidBodyAssignID')
    options.remove('YoubotBaseBattery')
    options.remove('YoubotBaseComputer')
    options.remove('AdafruitDCHatCore')

    # XXX: this should not be case-sensitive
#     options.remove('raspberryPI2')  # does not compile
#     options.remove('DaguChassis')
    options.remove('IRobotCreate')
    options.remove('YoubotBase')
    options.remove('duckiebot1')
    options.remove('duckiebot1_flatten')
    print('libraries: %s' % libnames)
    print('options: %s' % options)

    initial_string = """
        mcdp {    
            provides motion [`Motion]
            
            assign_id = instance abstract `RigidBodyAssignID
            
            add_budget = instance abstract mcdp {    
                provides budget1 [USD]
                provides budget2 [USD]
                provides budget3 [USD]
                provides budget4 [USD]
                provides budget5 [USD]
                provides budget6 [USD]
            
                requires budget [USD]
            
                required budget >= (
                    provided budget1 + 
                    provided budget2 +
                    provided budget3 +
                    provided budget4 +
                    provided budget5 +   
                    provided budget6 
                )
            }
            
            requires budget >= budget required by add_budget
            requires ac [`AC_charging]
        }
    """
    

    poset = library.parse_poset


    flabels, F0s, f0s = zip(*(
        ('motion', poset('`Motion'), ('rb1', 0.1, 600.0)),
    ))

    rlabels, R0s, r0s = zip(*(
        ('ac', poset('`AC_Charging'), 
         (('AC_power', 'TypeA', 'v110', 'f50', 200.0), 3 * 3600.0)),
        ('budget', poset('USD'), 1000.0),
    ))

    initial = library.parse_ndp(initial_string)

    opt = Optimization(library=library, options=options,
                       flabels=flabels, F0s=F0s, f0s=f0s,
                       rlabels=rlabels, R0s=R0s, r0s=r0s,
                       initial=initial)

    i = 0
    maxit = 500
    out_draw_tree = os.path.join(outdir, 'optim_tree')
    if os.path.exists(out_draw_tree):
        shutil.rmtree(out_draw_tree)

    while not opt.is_done() and i <= maxit:
        opt.step()
        opt.print_status()
        opt.draw_tree(out_draw_tree)
        i += 1

    opt.print_status()

    r = Report()

    for i, state in enumerate(opt.done):
        ndp = state.get_current_ndp()
        plot_ndp(r, 'done%d' % i, ndp, library)

    for i, state in enumerate(opt.states):
        ndp = state.get_current_ndp()
        with r.subsection('open%d' % i) as s:
            plot_ndp(s, 'open%d' % i, ndp, library)
            msg = 'ur: %s' % state.ur
            msg += '\n num_connection_options: %s' % state.num_connection_options
            s.text('info', msg)

    for i, state in enumerate(opt.abandoned):
        with r.subsection('abandoned%d' % i) as s:
            ndp = state.get_current_ndp()
            plot_ndp(s, 'abandoned%d' % i, ndp, library)
            msg = getattr(state, 'msg', '(no message)')

            msg += '\n ur: %s' % state.ur
            msg += '\n num_connection_options: %s' % state.num_connection_options
            s.text('info', msg)

    fn = os.path.join(outdir, 'opt_basic_1.html')
    print(fn)
    r.to_html(fn)


def plot_ndp(r, name, ndp, library):

    ndp = cndp_templatize_children(ndp)

    images_paths = library.get_images_paths()

    setattr(ndp, '_hack_force_enclose', True)
    gg = gvgen_from_ndp(ndp, style=STYLE_GREENREDSYM,
                        images_paths=images_paths)
    gg_figure(r, name, gg,
               do_pdf=False, do_svg=False,
              do_dot=False)
    
    
@comptest
def opt_basic_2():
    l1 = parse_poset('J').U(1.0)
    l2 = parse_poset('m x J').U((1.0, 1.0))
    n1 = (1,)
    n2 = (1,)
    N = PosetProduct((Nat(),))

    # create a joint one
    l1b = add_extra(l1, N, n1)
    l2b = add_extra(l2, N, n2)

    print l1b
    print l2b

    assert less_resources2(l1b, l2b)
    assert not less_resources2(l2b, l1b)

@contract(lb=UpperSet, P=Poset, returns=UpperSet)
def add_extra(lb, P, v):
    P.belongs(v)
    P1 = lb.P
    if not isinstance(P1, PosetProduct):
        P1 = PosetProduct((P1,))
        minimals = set((a,) for a in lb.minimals)
    else:
        minimals = lb.minimals
    P1b = PosetProduct(P1.subs + (P,))
    def mm(x):
        return x + (v,)
    l1b = P1b.Us(map(mm, minimals))
    return l1b


@comptest
def opt_basic_3():
    l1b = parse_constant('upperclosure { < 10 g > }').value
    l2b = parse_constant('upperclosure { < 20 g > }').value
    assert less_resources2(l1b, l2b)
    assert not less_resources2(l2b, l1b)

    l1b = parse_constant('upperclosure { < 10 g > }').value
    l2b = parse_constant('upperclosure { < 20 mg > }').value
    assert not less_resources2(l1b, l2b)
    assert  less_resources2(l2b, l1b)


@comptest
def opt_basic_4():
    l1b = parse_constant('upperclosure { < 10 g, 2 J > }').value
    l2b = parse_constant('upperclosure { < 2 J, 20 mg > }').value

    assert not less_resources2(l1b, l2b)
    assert less_resources2(l2b, l1b)

@comptest_fails
def opt_basic_5():
    """ It should be able to re-order, but it doesn't.... """
    l1b = parse_constant('upperclosure { < 1 g, 4 g > }').value
    l2b = parse_constant('upperclosure { < 5 g, 3 g > }').value

    assert not less_resources2(l1b, l2b)
    assert less_resources2(l2b, l1b)

@comptest
def opt_basic_6():
    libnames = ['actuation']
    library = get_test_library2(libnames)

    outdir = 'out/opt_basic_6'

    library.use_tmp_cache()
    
    options = ['DaguChassis', 'AdaFruitDCHat0',
               'BatteryRavpower', 'USB_to_barrel',
               'USBMicroCharging']

    for o in options:
        print('Trying if %r is connected...' % o)
        ndp = library.load_ndp(o)
        _dp = ndp.get_dp()

    initial_string = """
        mcdp {    
            provides motion [`Motion]
            
            assign_id = instance abstract `RigidBodyAssignID
            
            add_budget = instance abstract mcdp {    
                provides budget1 [USD]
                provides budget2 [USD]
                provides budget3 [USD]
                provides budget4 [USD]
                provides budget5 [USD]
                provides budget6 [USD]
                provides budget7 [USD]
            
                requires budget [USD]
            
                required budget >= (
                    provided budget1 + 
                    provided budget2 +
                    provided budget3 +
                    provided budget4 +
                    provided budget5 +
                    provided budget6 +
                    provided budget7
                )
            }
            
            requires budget >= budget required by add_budget
            requires ac [`AC_charging]
        }
    """

    min_functions = {
        'motion': '< `RigidBodyID: rb1, 0.1 m/s, 10 minutes >',
    }
    max_resources = {
        'ac': '<<`socket_type: TypeA, `AC_voltages: v110, `AC_frequencies: f50, 50W>, 3600 s>',
        'budget': '1000 USD',
    }

    flabels, F0s, f0s = _parse_dict(min_functions, library)
    rlabels, R0s, r0s = _parse_dict(max_resources, library)

    initial = library.parse_ndp(initial_string)

    opt = Optimization(library=library, options=options,
                       flabels=flabels, F0s=F0s, f0s=f0s,
                       rlabels=rlabels, R0s=R0s, r0s=r0s,
                       initial=initial)

    i = 0
    maxit = 2000
    out_draw_tree = os.path.join(outdir, 'optim_tree')
    if os.path.exists(out_draw_tree):
        shutil.rmtree(out_draw_tree)

    while not opt.is_done() and i <= maxit:
        opt.print_status()
        opt.step()
        opt.draw_tree(out_draw_tree)
        i += 1

    opt.print_status()


def _parse_dict(d, library):
    labels = []
    posets = []
    values = []
    for f, fv in d.items():
        c = library.parse_constant(fv)
        labels.append(f)
        posets.append(c.unit)
        values.append(c.value)
    return tuple(labels), tuple(posets), tuple(values)

# @comptest
mcdp_dev_warning('temporarily disabled opt_basic_7()')

def opt_basic_7():
    libnames = ['actuation']
    library = get_test_library2(libnames)

#     outdir = 'out/opt_basic_7'
#     cache_dir = os.path.join(outdir, 'cache')
    library.use_tmp_cache()
    ndp = library.load_ndp('duckiebot_sol00')


    min_functions = {
        'motion': '< `RigidBodyID: rb1, 0.1 m/s, 10 minutes >',
    }
    _flabels, F0s, f0s = _parse_dict(min_functions, library)

    names = [name for name, _ndp in cndp_get_name_ndp_notfunres(ndp)]
    print('names: %s' % names)

    to_remove = list(names)
    to_remove.remove('dagu_chassis')
    # to_remove.remove('battery_ravpower')
    # to_remove.remove('USBMicroCharging')

    from mcdp_opt_tests.ndp_utils import cndp_remove_one_child
    for n in to_remove:
        ndp = cndp_remove_one_child(ndp, n)

    print ndp


    if len(F0s) > 1:
        F = PosetProduct(F0s)
        f0 = f0s
    else:
        F = F0s[0]
        f0 = f0s[0]

    dp = ndp.get_dp()
    F1 = dp.get_fun_space()

    f1 = express_value_in_isomorphic_space(F, f0, F1)

    _res = dp.solve(f1)
    #print res
 

@comptest
def opt_basic_8():
    libnames = ['actuation']
    library = get_test_library2(libnames)

    outdir = 'out/opt_basic_8'
    cache = os.path.join(outdir, 'cache')
    print('using cache %s' % cache)
    library.use_cache_dir(cache)

    ndp = library.load_ndp('DaguChassis')
    R = ndp.get_rtype('pwm1')
    assert getattr(R, MCDPConstants.ATTR_LOAD_NAME) == 'PWM'

    ndp = library.load_ndp('DaguChassis')
    R = ndp.get_rtype('pwm1')
    assert getattr(R, MCDPConstants.ATTR_LOAD_NAME) == 'PWM'
