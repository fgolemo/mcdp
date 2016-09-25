import itertools

import numpy as np
from reprep.plot_utils.spines import set_spines_look_A


def plot_field(pylab, x, y, z, cmap, zoom=1, vmin=None, vmax=None):

    def value_at(cx, cy):
        for x0, y0, z0 in itertools.product(x, y, z):
            if cx == x0 and cy == y0:
                return z0
        raise ValueError((cx, cy))

    xu = np.sort(np.unique(x))
    yu = np.sort(np.unique(y))

    xu = np.linspace(xu[0], xu[-1], len(xu) * zoom)
    yu = np.linspace(yu[0], yu[-1], len(xu) * zoom)

    X, Y = np.meshgrid(xu, yu)

    from matplotlib.mlab import griddata
    resampled = griddata(x, y, z, xu, yu, interp='linear')

    pylab.pcolor(X, Y, resampled,  vmin=vmin, vmax=vmax,
                 cmap=cmap) 
    
def ieee_spines_zoom3(pylab):
    z = 3
    set_spines_look_A(pylab, outward_offset=5 * z,
                      linewidth=1 * z, markersize=2 * z, markeredgewidth=0.5 * z)


def ieee_fonts_zoom3(pylab):
    # See http://matplotlib.sourceforge.net/users/customizing.html#matplotlibrc-sample
    z = 3
    params = {
#             'text.usetex': True,
          'axes.labelsize': 10 * z,
#           'text.fontsize': 8,
#           'font.size': 12 * z,
          'legend.fontsize': 7 * z,
          'axes.titlesize': 10 * z,

          'lines.markersize': 3 * z,
          'lines.markeredgewidth': 0.5 * z,

          # lines.markeredgewidth  : 0.5     # the line width around the marker symbol
# lines.markersize  : 6            # markersize, in points

          'axes.linewidth': 1 * z,
          'axes.color_cycle': ['k', 'm', 'g', 'c', 'm', 'y', 'k'],
          'legend.fancybox': True,
          'legend.frameon': False,
          'legend.numpoints': 1,
          'legend.markerscale': 2,
          'legend.labelspacing': 0.2,
          'legend.columnspacing': 1,
          'legend.borderaxespad': 0.1,
          'errorbar.capsize' : 3 * z,
        'xtick.labelsize': 8 * z,
        'xtick.major.size'     : 6 * z,  # major tick size in points
        'xtick.minor.size'     : 4 * z,  # minor tick size in points
        'xtick.major.width'    : 0.5 * z,  # major tick width in points
        'xtick.minor.width'    : 0.5 * z,  # minor tick width in points
        'xtick.major.pad'      : 4 * z,  # distance to major tick label in points
        'xtick.minor.pad'      : 4 * z,

          'ytick.labelsize': 8 * z,
        'ytick.major.size'     : 4 * z,  # major tick size in points
        'ytick.minor.size'     : 2 * z,  # minor tick size in points
        'ytick.major.width'    : 0.5 * z,  # major tick width in points
        'ytick.minor.width'    : 0.5 * z,  # minor tick width in points
        'ytick.major.pad'      : 4 * z,  # distance to major tick label in points
        'ytick.minor.pad'      : 4 * z,

    }
    pylab.rcParams.update(params)

    from matplotlib import rc
    # cmr10 works but no '-' sign
    rc('font', **{'family': 'serif',
                 'serif': ['Times', 'Times New Roman',
                           'Bitstream Vera Serif',
                           'Palatino'],
#                   'size': 16.0
                  })
