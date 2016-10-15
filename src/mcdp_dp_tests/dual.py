from mcdp_dp.primitive import NotSolvableNeedsApprox
from mcdp_posets.uppersets import LowerSets
from mcdp_posets.utils import poset_check_chain
from mcdp_tests.generation import for_all_dps
from mcdp_posets.space import NotBelongs
from contracts.utils import raise_wrapped


@for_all_dps
def dual01_chain(_, dp):
    
    # get a chain of resources
    R = dp.get_res_space()
    rchain = R.get_test_chain(n=5)
    poset_check_chain(R, rchain)

    try:
        lfchain = list(map(dp.solve_r, rchain))
    except NotSolvableNeedsApprox as e:
        print('skipping because %s'  % e)
        return

    F = dp.get_fun_space()
    LF = LowerSets(F)
    
    poset_check_chain(LF, list(reversed(lfchain)))


    # now, for each functionality f, 
    # we know that the corresponding resource should be feasible
    for lf, r in zip(lfchain, rchain):
        for f in lf.maximals:
            f_ur = dp.solve(f)
            try:
                f_ur.belongs(r)
            except NotBelongs as e:
                msg = 'Point does not belong.'
                raise_wrapped(AssertionError, e, msg,
                              lf=lf, r=r, f_ur=f_ur)
            

@for_all_dps
def dual02(_, dp):
    
    pass

@for_all_dps
def dual03(_, dp):
    pass

@for_all_dps
def dual04(_, dp):
    pass

@for_all_dps
def dual05(_, dp):
    pass

@for_all_dps
def dual06(_, dp):
    pass

@for_all_dps
def dual07(_, dp):
    pass

@for_all_dps
def dual08(_, dp):
    pass

@for_all_dps
def dual09(_, dp):
    pass

@for_all_dps
def dual10(_, dp):
    pass

@for_all_dps
def dual11(_, dp):
    pass

@for_all_dps
def dual12(_, dp):
    pass

@for_all_dps
def dual13(_, dp):
    pass


