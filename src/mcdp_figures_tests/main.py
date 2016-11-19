from comptests.registrar import comptest
from mcdp_lang.parse_interface import parse_ndp
from mcdp_figures.figure_interface import MakeFiguresNDP
from mcdp_tests.generation import for_all_nameddps_dyn
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


@for_all_nameddps_dyn
def allformats(context, id_ndp, ndp, libname):
    r = context.comp(allformats_report, id_ndp, ndp, libname)
    context.add_report(r, 'allformats', id_ndp=id_ndp)
    
def allformats_report(id_ndp, ndp, libname):
    from mcdp_web.images.images import get_mime_for_format

    r = Report()
    mf = MakeFiguresNDP(ndp=ndp, library=None, yourname=None)
    for name in mf.available():
        formats = mf.available_formats(name)
        res = mf.get_figure(name, formats)
        print('%s -> %s %s ' % (name, formats, map(len, [res[f] for f in formats])))
        for f, data in zip(formats, res):
            mime = get_mime_for_format(f)
            dn = DataNode(f, data=data, mime=mime)
            r.add_child(dn)
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