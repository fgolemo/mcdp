# -*- coding: utf-8 -*-
from contracts.utils import raise_wrapped
from mcdp_dp import NotSolvableNeedsApprox
from mcdp_posets import LowerSets, UpperSets
from mcdp_posets import NotBelongs
from mcdp_posets.rcomp import Rcomp
from mcdp_posets.utils import poset_check_chain
from mcdp_tests.generation import for_all_dps, primitive_dp_test
from mocdp import logger
import numpy as np


@for_all_dps
def dual01_chain(id_dp, dp):
    try:
        with primitive_dp_test(id_dp, dp):
            # get a chain of resources
            F = dp.get_fun_space()
            R = dp.get_res_space()
            LF = LowerSets(F)
            UR = UpperSets(R)
        
            rchain = R.get_test_chain(n=5)
            poset_check_chain(R, rchain)
        
            try:
                lfchain = list(map(dp.solve_r, rchain))
                for lf in lfchain:
                    LF.belongs(lf)
            except NotSolvableNeedsApprox as e:
                print('skipping because %s'  % e)
                return
        
            
            poset_check_chain(LF, list(reversed(lfchain)))
        
            # now, for each functionality f, 
            # we know that the corresponding resource should be feasible
            
            for lf, r in zip(lfchain, rchain):
                print('')
                print('r: %s' % R.format(r))
                print('lf = h*(r) = %s' % LF.format(lf))
                
                for f in lf.maximals:
                    print('  f = %s' % F.format(f))
                    f_ur = dp.solve(f)
                    print('  f_ur = h(f) =  %s' % UR.format(f_ur))
                     
                    try:
                        f_ur.belongs(r)
                    except NotBelongs as e:
                        
                        try:
                            Rcomp.tolerate_numerical_errors = True
                            f_ur.belongs(r)
                            logger.info('In this case, there was a numerical error')
                            logger.info('Rcomp.tolerate_numerical_errors = True solved the problem')                    
                        except:
                            msg = ''
                            raise_wrapped(AssertionError, e, msg,
                                          lf=lf, r=r, f_ur=f_ur,
                                          r_repr=r.__repr__(),
                                          f_ur_minimals=f_ur.minimals.__repr__())
    finally:
        Rcomp.tolerate_numerical_errors = False
            
            
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


