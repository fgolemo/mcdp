from contracts import contract
from matplotlib.cm import get_cmap
from reprep.plot_utils.styles import ieee_spines
from mcdp_ipython_utils.loading import to_numpy_array
from reprep.plot_utils.axes import y_axis_extra_space, x_axis_extra_space
def generate_colors(n, colormap_name):
    """ Generates n color strings. """
#     from itertools import cycle
#     cycol = cycle('bgrcmk').next
#     colors = [cycol() for _ in range(n)]

    colors = []
    cm = get_cmap(colormap_name)
    for i in range(n):
        color = cm(1.*i / n)  # color will now be an RGBA tuple
        colors.append(color)

    return colors



@contract(queries='list[N](dict)', results='list[N](list(dict))',
          what_to_plot_fun='dict', what_to_plot_res='dict')
def plot_all_directions(r, queries, results, what_to_plot_fun, what_to_plot_res):
    """
        result_like 
        
        result_like = dict(maintenance="s", cost="$", mass='kg')
    """
    n = len(queries)
    assert n == len(results)
    colors = generate_colors(n, colormap_name='Paired')

    import itertools
    #

    for xwhat, ywhat in itertools.combinations(what_to_plot_res, 2):
        name = '%s_%s' % (xwhat, ywhat)
        with r.plot(name) as pylab:
            plot_axis(pylab, results, what_to_plot_res, colors, xwhat, ywhat,
                      marker='s')
            set_axis_colors(pylab, '#700000')

    for xwhat, ywhat in itertools.combinations(what_to_plot_fun, 2):
        name = '%s_%s' % (xwhat, ywhat)
        with r.plot(name) as pylab:
            qqueries = [ [ x ] for x in queries]
            plot_axis(pylab, qqueries, what_to_plot_fun, colors, xwhat, ywhat,
                      marker='o')

            set_axis_colors(pylab, '#007000')

def set_axis_colors(pylab, color):
    ax = pylab.gca()

    ax.spines['bottom'].set_color(color)
    ax.spines['left'].set_color(color)
    ax.xaxis.label.set_color(color)
    ax.tick_params(axis='x', colors=color)
    ax.yaxis.label.set_color(color)
    ax.tick_params(axis='y', colors=color)


def plot_axis(pylab, results, what_to_plot, colors, xwhat, ywhat, marker):
#     print results , what_to_plot

    f = pylab.gcf()
    size = 1.57 * 3
    ratio = 1
    f.set_size_inches((size, size * ratio))
    ieee_spines(pylab)

    def s(what) :
        if what_to_plot[what] == '[]':
            return what
        st = '%s [%s]' % (what, what_to_plot[what])
        st.replace('$', '\\$')
        return st

    for res, color in zip(results, colors):
        a = to_numpy_array(what_to_plot, res)
        x = a[xwhat]
        y = a[ywhat]
        pylab.plot(x, y, marker, color=color)

    pylab.xlabel(s(xwhat))
    pylab.ylabel(s(ywhat))
    y_axis_extra_space(pylab)
    x_axis_extra_space(pylab)
