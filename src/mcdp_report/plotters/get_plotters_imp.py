from contracts.utils import raise_desc, indent
from mcdp_report.plotters.interface import NotPlottable

def get_all_available_plotters():
    from mcdp_report.plotters.plotter_ur2 import PlotterUR2
    from mcdp_report.plotters.plotter_ur import PlotterUR
    from mcdp_report.plotters.plotter_bounds import Plotter_Tuple2_UR2
    from mcdp_report.plotters.plotter_urr import PlotterURRpR_12, PlotterURRpR_13,\
        PlotterURRpR_23

    plotters = {
       'PlotterUR2': PlotterUR2(),
       'PlotterUR': PlotterUR(),
         'Tuple2_UR2': Plotter_Tuple2_UR2(),
        'URRpR_12': PlotterURRpR_12(),
        'URRpR_13': PlotterURRpR_13(),
        'URRpR_23': PlotterURRpR_23(),
    }
    return plotters

def get_best_plotter(space):
    p = list(get_plotters(get_all_available_plotters(), space))
    if not p:
        msg = 'Could not find any plotter for space %s.' % space
        raise_desc(ValueError, msg, space=space)
        
    return p[0][1]

def get_plotters(plotters, space):
    available = []
    errors = []
    for name, plotter in plotters.items():
        try:
            plotter.check_plot_space(space)
            available.append((name, plotter))
        except NotPlottable as e:
            errors.append((name, plotter, e))
    if available:
        return available
    msg = 'Could not find any plotter for space %s.' % space
    msg += '\n None of these worked: %s' % plotters.keys()
    msg += '\nTraceback:'
    for name, plotter, e in errors:
        msg += '\n%r (%s)\n%s' % (name, type(plotter), indent(str(e), '  '))
    raise_desc(NotPlottable, msg)
