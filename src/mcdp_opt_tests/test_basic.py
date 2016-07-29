from comptests.registrar import comptest
from mcdp_library import MCDPLibrary
from mcdp_library.utils import dir_from_package_name
from mcdp_opt.optimization import Optimization
from mcdp_report.gdc import STYLE_GREENREDSYM
from mcdp_report.gg_ndp import gvgen_from_ndp
from mcdp_report.gg_utils import gg_figure
from mcdp_web.main import load_libraries
from mocdp.comp.composite_templatize import cndp_templatize_children
from reprep import Report
import os

def get_test_library(libnames):
    package = dir_from_package_name('mcdp_data')
    libraries = os.path.join(package, 'libraries')
    d = load_libraries(libraries)
    
    l = MCDPLibrary()
    for lib in libnames:
        path = d[lib]['path']
        l.add_search_dir(path)

    l.use_cache_dir('out/mcdp_opt_tests_cache')
    return l

@comptest
def opt_basic_1():
    libnames = ['actuation']
    library = get_test_library(libnames)

    options = library.list_ndps()
    options.remove('DaguChassis')
#     options.remove('IRobotCreate')
    options.remove('YoubotBase')
    print('libraries: %s' % libnames)
    print('options: %s' % options)

    poset = library.parse_poset
#     value = library.parse_value

    flabels, F0s, f0s = zip(*(
        ('motion', poset('`Motion'), (0.1, 600.0)),
    ))

    rlabels, R0s, r0s = zip(*(
        ('ac', poset('`AC_Charging'), (('AC_power', 'TypeA', 'v110', 'f50', 200.0), 3 * 3600.0)),
        ('budget', poset('USD'), 1000.0),
    ))

    opt = Optimization(library=library, options=options,
                       flabels=flabels, F0s=F0s, f0s=f0s,
                       rlabels=rlabels, R0s=R0s, r0s=r0s)

    r = Report()

    i = 0
    maxit = 60
    while opt.states and i <= maxit:
        opt.print_status()
        opt.step()
        i += 1

    opt.print_status()

    for i, state in enumerate(opt.done):
        ndp = state.get_current_ndp()
        plot_ndp(r, 'done%d' % i, ndp, library)

    for i, state in enumerate(opt.states):
        ndp = state.get_current_ndp()
        plot_ndp(r, 'open%d' % i, ndp, library)

    for i, state in enumerate(opt.abandoned):
        with r.subsection('abandoned%d' % i) as s:
            ndp = state.get_current_ndp()
            plot_ndp(s, 'abandoned%d' % i, ndp, library)
            msg = getattr(state, 'msg', '(no message)')
            s.text('info', msg)



    fn = 'out/opt_basic_1.html'
    print fn
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
    pass


@comptest
def opt_basic_3():
    pass


@comptest
def opt_basic_4():
    pass


@comptest
def opt_basic_5():
    pass


@comptest
def opt_basic_6():
    pass

@comptest
def opt_basic_7():
    pass


@comptest
def opt_basic_8():
    pass
