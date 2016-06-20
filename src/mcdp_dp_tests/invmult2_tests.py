from comptests.registrar import comptest
from mcdp_lang.parse_interface import parse_poset
from mcdp_dp import InvMult2
from mcdp_dp.primitive import ApproximableDP
from mcdp_posets.uppersets import UpperSets


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

    for i in [1, 5, 10]:
        rl = iml.solve(i)
        ru = imu.solve(i)
        print UR.format(rl)
        print UR.format(ru)
        UR.check_leq(rl, ru)
        

@comptest
def invmult2_check2():
    pass


@comptest
def invmult2_check3():
    pass

@comptest
def invmult2_check4():
    pass


@comptest
def invmult2_check5():
    pass
    

