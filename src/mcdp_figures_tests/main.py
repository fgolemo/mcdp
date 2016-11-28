import random

from comptests.registrar import comptest
from mcdp_figures.figure_interface import MakeFiguresNDP
from mcdp_lang.parse_interface import parse_ndp
from mcdp_tests.generation import for_all_nameddps_dyn
from mocdp import MCDPConstants
from mocdp.exceptions import DPSemanticError
from reprep import Report
from reprep.datanode import DataNode


@comptest
def figint01():
    ndp = parse_ndp("""
        mcdp {
        
        }
    """)
    mf = MakeFiguresNDP(ndp=ndp, library=None, yourname=None)

    for name in mf.available():
        formats = mf.available_formats(name)
        res = mf.get_figure(name, formats)
        print('%s -> %s %s ' % (name, formats, map(len, [res[f] for f in formats])))

def toss_coin(h, prob_success):
    random.seed(h)
    u = random.uniform(0.0, 1.0)
    success = u >= 1 - prob_success 
    return success

@for_all_nameddps_dyn
def allformats(context, id_ndp, ndp, libname):
    mf = MakeFiguresNDP(ndp=ndp, library=None, yourname=None)
    for name in mf.available():
        
        do_it = libname in ['basic', 'libtemplates', 'solver'] or \
            toss_coin(id_ndp, MCDPConstants.test_fraction_of_allreports) 
        
        if do_it:
            r = context.comp(allformats_report, id_ndp, ndp, libname, name,
                             job_id=name)
            context.add_report(r, 'allformats', id_ndp=id_ndp, which=name)
    
def allformats_report(id_ndp, ndp, libname, which):
    from mcdp_web.images.images import get_mime_for_format
    r = Report(id_ndp + '-' + which)
    from mcdp_library_tests.tests import get_test_library
    library = get_test_library(libname)
    mf = MakeFiguresNDP(ndp=ndp, library=library, yourname=id_ndp)
    formats = mf.available_formats(which)
    try:
        res = mf.get_figure(which, formats)
    except DPSemanticError as e:
        if 'Cannot abstract' in str(e):
            r.text('warning', 'Not connected. \n\n %s' % e)
            return r
    print('%s -> %s %s ' % (which, formats, map(len, [res[f] for f in formats])))
    fig = r.figure()
    for f in formats:
        data = res[f]
        mime = get_mime_for_format(f)
        dn = DataNode(f, data=data, mime=mime)
        fig.add_child(dn)
    return r    
    
@comptest
def figint02():
    pass

@comptest
def figint03():
    pass

@comptest
def figint04():
    pass

@comptest
def figint05():
    pass

@comptest
def figint06():
    pass

@comptest
def figint07():
    pass

@comptest
def figint08():
    pass

@comptest
def figint09():
    pass

@comptest
def figint10():
    pass