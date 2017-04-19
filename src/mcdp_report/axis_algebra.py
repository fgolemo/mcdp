# -*- coding: utf-8 -*-
import numpy as np
from contracts import contract
from mcdp.exceptions import mcdp_dev_warning
from mcdp_posets.rcomp import finfo


def join_axes(a, b):
    return (min(a[0], b[0]),
            max(a[1], b[1]),
            min(a[2], b[2]),
            max(a[3], b[3]))
    
def enlarge_x(b, f):
    w = b[1] - b[0]
    # h = b[3] - b[2]
    dw = f * w
    dh = 0
    return (b[0] - dw, b[1] + dw, b[2] - dh, b[3] + dh)

def enlarge_y(b, f):
    # w = b[1] - b[0]
    h = b[3] - b[2]
    dw = 0
    dh = h * f
    return (b[0] - dw, b[1] + dw, b[2] - dh, b[3] + dh)

@contract(b='seq[4](float|int)', f='float,>=0')
def enlarge(b, f):
    w = b[1] - b[0]
    h = b[3] - b[2]
    # print b, f, w, h
    
    dw = fix_underflow(f) * fix_underflow(w)
    dh = fix_underflow(h) * fix_underflow(f)
    a = (b[0] - dw, b[1] + dw, b[2] - dh, b[3] + dh)
    
    return a

    mcdp_dev_warning('this is not correct (axis might be negative)')
    return tuple(map(fix_underflow, a))

def fix_underflow(x):
    # using finfo.tiny gives problems to matplotlib
    return np.maximum(x, finfo.eps)


def enlarge_topright(b, f):
    w = b[1] - b[0]
    h = b[3] - b[2]
    dw = f * w
    dh = h * f
    return (b[0], b[1] + dw, b[2], b[3] + dh)

def reduce_bounds(b1, b2):
    return (min(b1[0], b2[0]),
            max(b1[1], b2[1]),
            min(b1[2], b2[2]),
            max(b1[3], b2[3]))

def get_bounds(points):
    if not points:
        return (0, 0, 0, 0)
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    return (min_comp(xs, 0.0),
            max_comp(xs, 0.0),
            min_comp(ys, 0.0),
            max_comp(ys, 0.0))


def _get_finite(xs):
    return  [_ for _ in xs if isinstance(_, (int, float))]

def max_comp(xs, d):
    xs = _get_finite(xs)
    if not xs:
        return d
    return max(xs)

def min_comp(xs, d):
    xs = _get_finite(xs)
    if not xs:
        return d
    return min(xs)
