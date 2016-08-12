from comptests.registrar import comptest
from mcdp_library_tests.tests import get_test_library
from mocdp.comp.recursive_name_labeling import label_with_recursive_names, \
    get_imp_as_recursive_dict
from mcdp_cli.query_interpretation import convert_string_query
import os
from reprep import Report
from mcdp_report.gg_ndp import gvgen_from_ndp
from mcdp_report.gdc import STYLE_GREENREDSYM
from mcdp_report.gg_utils import gg_figure


@comptest
def check_ndp_grap_imp1():
    library = get_test_library('batteries_nodisc')
    out = 'out/check_ndp_grap_imp1'
    library.use_cache_dir(os.path.join(out, 'cache'))

    ndp = library.load_ndp('batteries')
    context = library._generate_context_with_hooks()
    label_with_recursive_names(ndp)
    dp = ndp.get_dp()

    M = dp.get_imp_space()

    query = dict(missions='600 []', capacity='100 mJ')
    f = convert_string_query(ndp=ndp, query=query, context=context)

    report = Report()

    res = dp.solve(f)
    print('num solutions: %s' % len(res.minimals))
    for ri, r in enumerate(res.minimals):
        ms = dp.get_implementations_f_r(f, r)

        for j, m in enumerate(ms):
            imp_dict = get_imp_as_recursive_dict(M, m)
            print imp_dict

            images_paths = library.get_images_paths()
            gg = gvgen_from_ndp(ndp=ndp, style=STYLE_GREENREDSYM, images_paths=images_paths)

            with report.subsection('%s-%s' % (ri, j)) as rr:
                gg_figure(rr, 'figure', gg, do_png=True, do_pdf=False, do_svg=False, do_dot=False)


    fn = os.path.join(out, 'solutions.html')
    print('writing to %s' % fn)
    report.to_html(fn)

@comptest
def check_ndp_grap_imp2():
    pass


@comptest
def check_ndp_grap_imp3():
    pass


@comptest
def check_ndp_grap_imp4():
    pass

