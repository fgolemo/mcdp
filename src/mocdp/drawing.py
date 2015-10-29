from contracts import contract
from mocdp.posets.uppersets import UpperSet
import warnings
from mocdp.exceptions import mcdp_dev_warning


def plot_upset_minima(pylab, us):
    points = us.minimals

    # write once for axis
    for p in points:
        pylab.plot(p[0], p[1], 'k.')


@contract(us=UpperSet)
def plot_upset_R2(pylab, us, axis, color_shadow, color_lines='none'):
    points = us.minimals

    xmin, xmax, ymin, ymax = axis
    for p in points:
        if xmin <= p[0] <= xmax and (ymin <= p[1] <= ymax):
            mcdp_dev_warning('This should be smarter')
            plot_cone(pylab, p, axis, color_shadow=color_shadow,
                      color_lines=color_lines)
    # cuteness
    for p in points:
        pylab.plot(p[0], p[1], 'k.')


def plot_cone(pylab, p, axis, color_shadow, color_lines):
    from matplotlib import patches
    [_, xmax, _, ymax] = axis

    ax1 = pylab.gca()
    ax1.add_patch(
    patches.Rectangle(
        p,  # (x,y)
        xmax - p[0],  # width
        ymax - p[1],  # height
        facecolor=color_shadow,
        edgecolor='none',
    ))
    pylab.plot([p[0], p[0]], [p[1], ymax], '-', color=color_lines)
    pylab.plot([p[0], xmax], [p[1], p[1]], '-', color=color_lines)






