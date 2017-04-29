from comptests.registrar import comptest
from mcdp import MCDPConstants
from mcdp.exceptions import DPSemanticError
from mcdp_figures import MakeFiguresNDP, MakeFiguresPoset
from mcdp_lang.parse_interface import parse_ndp
from mcdp_report.image_source import ImagesFromPaths
from mcdp_tests.generation import for_all_nameddps_dyn, for_all_posets
import random

from reprep import Report
from reprep.datanode import DataNode


@comptest
def figint01():
    ndp = parse_ndp("""
        mcdp {
        
        }
    """)
    mf = MakeFiguresNDP(ndp=ndp, image_source=None, yourname=None)

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
    mf = MakeFiguresNDP(ndp=ndp, image_source=None, yourname=None)
    for name in mf.available():
        
        do_it = libname in ['basic', 'libtemplates', 'solver'] or \
            toss_coin(id_ndp, MCDPConstants.test_fraction_of_allreports) 
        
        if do_it:
            r = context.comp(allformats_report, id_ndp, ndp, libname, name,
                             job_id=name)
            
            if MCDPConstants.test_allformats_report_write:
                context.add_report(r, 'allformats', id_ndp=id_ndp, which=name)


@for_all_posets
def allformats_posets(context, id_poset, poset, libname):
    mf = MakeFiguresPoset(poset=poset, image_source=None, yourname=None)
    for name in mf.available():
        do_it = libname in ['basic', 'libtemplates', 'solver'] or \
            toss_coin(id_poset, MCDPConstants.test_fraction_of_allreports) 
        
        if do_it:
            r = context.comp(allformats_posets_report, id_poset, poset, libname, name,
                             job_id=name)
            
            if MCDPConstants.test_allformats_report_write:
                context.add_report(r, 'allformats_posets', id_poset=id_poset, which=name)
    

def allformats_posets_report(id_poset, poset, libname, which):
    from mcdp_web.images.images import get_mime_for_format
    from mcdp_library_tests.tests import get_test_library
    r = Report(id_poset + '-' + which)
    library = get_test_library(libname)
    image_source = ImagesFromPaths(library.get_images_paths())
    mf = MakeFiguresPoset(poset=poset, image_source=image_source)
    formats = mf.available_formats(which)    
    res = mf.get_figure(which, formats)
    
    fig = r.figure()
    for f in formats:
        data = res[f]
        mime = get_mime_for_format(f)
        dn = DataNode(f, data=data, mime=mime)
        fig.add_child(dn)
    return r    

def allformats_report(id_ndp, ndp, libname, which):
    from mcdp_web.images.images import get_mime_for_format
    from mcdp_library_tests.tests import get_test_library
    r = Report(id_ndp + '-' + which)
    library = get_test_library(libname)
    image_source = ImagesFromPaths(library.get_images_paths())
    mf = MakeFiguresNDP(ndp=ndp, image_source=image_source, yourname=id_ndp)
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
    