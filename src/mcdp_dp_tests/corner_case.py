# -*- coding: utf-8 -*-
from comptests.registrar import comptest
from mcdp_dp import JoinNDP, MeetNDP
from mcdp_maps import ProductNNatMap
from mcdp_posets import Nat
from mcdp_posets_tests.utils import assert_belongs, assert_does_not_belong


@comptest
def check_product1():
    
    amap = ProductNNatMap(4)

    assert amap((1,3,4,5)) == 5*4*3
    
    # TODO: make separate tests
    
@comptest
def check_join_meet_1():
    # test meet 
    # ⟨f₁, f₂⟩ ⟼ { min(f₁, f₂) }
    # r ⟼  { ⟨r, ⊤⟩, ⟨⊤, r⟩ }
    
    N = Nat()
    dp = MeetNDP(2, N)
    lf = dp.solve_r(5)
    print('lf: {}'.format(lf))
    assert_belongs(lf, (10, 5))
    assert_belongs(lf, (5, 10))
    assert_does_not_belong(lf, (10, 10))
    
    Rtop = N.get_top()
    lf2 = dp.solve_r(Rtop)
    print('lf2: {}'.format(lf2))
    assert_belongs(lf2, (10, 10))
    assert_belongs(lf2, (Rtop, Rtop))
    
    lf3 = dp.solve_r(0)
    print('lf3: {}'.format(lf3))
    assert_belongs(lf3, (0, 0))
    assert_does_not_belong(lf3, (0, 1))
    assert_does_not_belong(lf3, (1, 0))
    
    
    #    Join ("max") of n variables. 
    #    ⟨f₁, …, fₙ⟩ ⟼ { max(f₁, …, fₙ⟩ }
    #    r ⟼ ⟨r, …, r⟩
    dp = JoinNDP(3, N)
    ur = dp.solve((10, 3, 3))
    assert_belongs(ur, 10)
    assert_does_not_belong(ur, 9)
    
    lf = dp.solve_r(10)
    assert_does_not_belong(lf, (0, 11, 0))
    assert_belongs(lf, (0, 10, 0))
    assert_belongs(lf, (0, 9, 0))
    
    
