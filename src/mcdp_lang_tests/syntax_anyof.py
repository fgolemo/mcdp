# -*- coding: utf-8 -*-
from comptests.registrar import comptest
from mcdp_lang import parse_ndp
from mcdp_posets import LowerSet, UpperSet, UpperSets


@comptest
def check_anyof1():  
    ndp = parse_ndp("""
        mcdp {
            requires x [g x g]
            
            x >= any-of({<0g,1g>, <1g, 0g>})
        }
    """)
    dp = ndp.get_dp()
    R = dp.get_res_space()
    UR = UpperSets(R)
    res = dp.solve(())
    UR.check_equal(res, UpperSet([(0.0,1.0),(1.0,0.0)], R))


@comptest
def check_anyof2(): 
    ndp = parse_ndp("""
        mcdp {
            provides x [g x g]
            
            x <= any-of({<0g,1g>, <1g, 0g>})
        }
    """)
    dp = ndp.get_dp()
    R = dp.get_res_space()
    F = dp.get_fun_space()
    UR = UpperSets(R)
    res = dp.solve((0.5, 0.5))

    l = LowerSet(P=F, maximals=[(0.0, 1.0), (1.0, 0.0)])
    l.belongs((0.0, 0.5))
    l.belongs((0.5, 0.0))

    UR.check_equal(res, UpperSet([], R))
    res = dp.solve((0.0, 0.5))

    UR.check_equal(res, UpperSet([()], R))
    res = dp.solve((0.5, 0.0))

    UR.check_equal(res, UpperSet([()], R))
