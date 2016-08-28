from comptests.registrar import comptest
from mcdp_dp import InvMult2
from mcdp_dp.dp_inv_plus import InvPlus2
from mcdp_dp.primitive import ApproximableDP
from mcdp_lang.parse_interface import parse_poset
from mcdp_posets.poset import NotLeq
from mcdp_posets.uppersets import UpperSets
from mcdp_posets.utils import check_minimal
from numpy.testing.utils import assert_allclose
from reprep import Report
import numpy as np

@comptest
def invmult2_check1():
    
    F = parse_poset('m')
    R1 = parse_poset('m/s')
    R2 = parse_poset('s')
    
    im = InvMult2(F, (R1, R2))
    assert isinstance(im, ApproximableDP)
    n = 4
    iml = im.get_lower_bound(n)
    imu = im.get_upper_bound(n)

    UR = UpperSets(im.get_res_space())

    for i in [1.0, 5.0, 10.0]:
        rl = iml.solve(i)
        ru = imu.solve(i)
        print UR.format(rl)
        print UR.format(ru)
        UR.check_leq(rl, ru)
        

@comptest
def invmult2_check2():
    
    F = parse_poset('m')
    R1 = parse_poset('m')
    R2 = parse_poset('m')
    
    im = InvPlus2(F, (R1, R2))

    R = im.get_res_space()
    UR = UpperSets(R)

    ns = [1, 2, 3, 4, 10, 15]
    resL = []
    resU = []
    f0 = 1.0
    for n in ns:
        dpU = im.get_upper_bound(n)
        dpL = im.get_lower_bound(n)
        urL = dpL.solve(f0)
        urU = dpU.solve(f0)
        UR.belongs(urL)
        UR.belongs(urU)
        resL.append(urL)
        resU.append(urU)

    r = Report()
    f = r.figure()
    for n, ur in zip(ns, resL):
        with f.plot('resL-%d' % n) as pylab:
            for n0, ur0 in zip(ns, resL):
                if n0 == n: continue
                points = np.array(list(ur0.minimals))
                pylab.plot(points[:, 0], points[:, 1], 'kx')

            points = np.array(list(ur.minimals))
            pylab.plot(points[:, 0], points[:, 1], 'o')
            pylab.axis((-0.1, 1.1, -0.1, 1.1))

    f = r.figure()
    for n, ur in zip(ns, resU):
        with f.plot('resU-%d' % n) as pylab:
            for n0, ur0 in zip(ns, resU):
                if n0 == n: continue
                points = np.array(list(ur0.minimals))
                pylab.plot(points[:, 0], points[:, 1], 'kx')

            points = np.array(list(ur.minimals))
            pylab.plot(points[:, 0], points[:, 1], 'o')
            pylab.axis((-0.1, 1.1, -0.1, 1.1))

    fn = 'out/invmult2_check2.html'
    print('writing to %s' % fn)
    r.to_html(fn)

    for urU in resU:
        for x, y in urU.minimals:
            assert x + y >= f0, (x, y, f0)
    for urL in resL:
        for x, y in urL.minimals:
            assert x + y <= f0, (x, y, f0)


    # check resU is DECREASING
    for i in range(len(resU) - 1):
        ur0 = resU[i]
        ur1 = resU[i + 1]
        try:
            UR.check_leq(ur1, ur0)
        except NotLeq:
            print('ur[%s]: %s ' % (i, UR.format(ur0)))
            print('ur[%s]: %s ' % (i + 1, UR.format(ur1)))
            raise Exception()

    # check resL is INCREASING
    for i in range(len(resU) - 1):
        ur0 = resL[i]
        ur1 = resL[i + 1]
        try:
            UR.check_leq(ur0, ur1)
        except NotLeq:
            print 'resL is not INCREASING'
            print('ur[%s]: %s x' % (i, UR.format(ur0)))
            print('ur[%s]: %s x ' % (i + 1, UR.format(ur1)))
            raise
            raise Exception('resL is not INCREASING')

    for ur0, ur1 in zip(resL, resU):
        UR.check_leq(ur0, ur1)


@comptest
def invmult2_check3():

    F = parse_poset('R')
    R1 = parse_poset('R')
    R2 = parse_poset('R')

    im = InvMult2(F, (R1, R2))

    InvMult2.ALGO = InvMult2.ALGO_VAN_DER_CORPUT

    R = im.get_res_space()
    UR = UpperSets(R)

#     ns = [1, 2, 3, 4, 10, 15]
#     ns = [1, 5, 10, 15, 25, 50, 61, 100]
    ns = [1, 2, 3, 4, 5, 10]
    resL = []
    resU = []
    f0 = 1.0
    for n in ns:
        dpU = im.get_upper_bound(n)
        dpL = im.get_lower_bound(n)
        urL = dpL.solve(f0)
        print urL
        print '%r' % urL.minimals
        check_minimal(urL.minimals, R)
        urU = dpU.solve(f0)
        check_minimal(urU.minimals, R)
        UR.belongs(urL)
        UR.belongs(urU)
        resL.append(urL)
        resU.append(urU)

    def plot_upper(pylab, ur, markers):
        points = np.array(list(ur.minimals))
        eps = np.finfo(float).eps
        points = np.maximum(points, eps)
        points = np.minimum(points, 20)

        pylab.plot(points[:, 0], points[:, 1], markers)

    r = Report()
    f = r.figure()
    for n, ur in zip(ns, resL):
        caption = str(ur)
        with f.plot('resL-%d' % n, caption=caption) as pylab:
            for n0, ur0 in zip(ns, resL):
                if n0 == n: continue
                plot_upper(pylab, ur0, 'kx')

            plot_upper(pylab, ur, 'o')

            pylab.axis((-0.1, 10.1, -0.1, 10.1))

    f = r.figure()
    for n, ur in zip(ns, resU):
        with f.plot('resU-%d' % n) as pylab:
            for n0, ur0 in zip(ns, resU):
                if n0 == n: continue
                plot_upper(pylab, ur0, 'kx')

            plot_upper(pylab, ur, 'o')
            pylab.axis((-0.1, 10.1, -0.1, 10.1))

    fn = 'out/invmult2_check3.html'
    print('writing to %s' % fn)
    r.to_html(fn)

    for urU in resU:
        for x, y in urU.minimals:
            prod = x * y
            if prod > f0:
                continue
            else:
                assert_allclose(x * y, f0)  # , (x, y, f0, x * y)
    for urL in resL:
        for x, y in urL.minimals:
            x = float(x)
            y = float(y)
            assert x * y <= f0, (x, y, f0, x * y)

    # check resU is DECREASING
    for i in range(len(resU) - 1):
        ur0 = resU[i]
        ur1 = resU[i + 1]
        try:
            UR.check_leq(ur1, ur0)
        except NotLeq:
            print('ur[%s]: %s ' % (i, UR.format(ur0)))
            print('ur[%s]: %s ' % (i + 1, UR.format(ur1)))
            raise Exception('resU is not DECREASING')

    # check resL is INCREASING
    for i in range(len(resU) - 1):
        ur0 = resL[i]
        ur1 = resL[i + 1]
        try:
            UR.check_leq(ur0, ur1)
        except NotLeq:
            print 'resL is not INCREASING'
            print('ur[%s]: %s x' % (i, UR.format(ur0)))
            print('ur[%s]: %s x ' % (i + 1, UR.format(ur1)))
            raise
            raise Exception('resL is not INCREASING')

    for ur0, ur1 in zip(resL, resU):
        UR.check_leq(ur0, ur1)

@comptest
def invmult2_check4():
    pass


@comptest
def invmult2_check5():
    pass
    

