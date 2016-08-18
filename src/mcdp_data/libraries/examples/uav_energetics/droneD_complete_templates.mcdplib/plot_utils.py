from reprep.plot_utils.spines import set_spines_look_A


def ieee_spines_zoom3(pylab):
    z = 3
    set_spines_look_A(pylab, outward_offset=5 * z,
                      linewidth=1 * z, markersize=2 * z, markeredgewidth=0.5 * z)


def ieee_fonts_zoom3(pylab):
    # See http://matplotlib.sourceforge.net/users/customizing.html#matplotlibrc-sample
    z = 3
    params = {
          'axes.labelsize': 8 * z,
#           'text.fontsize': 8,
          'font.size': 8 * z,
          'legend.fontsize': 8 * z,
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
        'xtick.labelsize': 6 * z,
        'xtick.major.size'     : 6 * z,  # major tick size in points
        'xtick.minor.size'     : 4 * z,  # minor tick size in points
        'xtick.major.width'    : 0.5 * z,  # major tick width in points
        'xtick.minor.width'    : 0.5 * z,  # minor tick width in points
        'xtick.major.pad'      : 4 * z,  # distance to major tick label in points
        'xtick.minor.pad'      : 4 * z,

          'ytick.labelsize': 6 * z,
        'ytick.major.size'     : 4 * z,  # major tick size in points
        'ytick.minor.size'     : 2 * z,  # minor tick size in points
        'ytick.major.width'    : 0.5 * z,  # major tick width in points
        'ytick.minor.width'    : 0.5 * z,  # minor tick width in points
        'ytick.major.pad'      : 4 * z,  # distance to major tick label in points
        'ytick.minor.pad'      : 4 * z,

#          'font.family': 'Times New Roman',
#          'font.serif': ['Times New Roman', 'Times'],
#          'font.size': 8
    #      'text.usetex': True
    }
    pylab.rcParams.update(params)

    from matplotlib import rc
    # cmr10 works but no '-' sign
    rc('font', **{'family': 'serif',
                 'serif': ['Bitstream Vera Serif', 'Times New Roman',
                           'Palatino'],
                  'size': 8.0})
