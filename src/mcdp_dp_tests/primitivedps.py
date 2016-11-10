# -*- coding: utf-8 -*-
from mcdp_dp import (CatalogueDP, CoProductDP, CoProductDPLabels, Constant,
    ConstantMinimals, DPLoop2, Identity, InvMult2, InvMult2L, InvMult2U,
    InvPlus2, InvPlus2L, InvPlus2Nat, InvPlus2U, JoinNDP, Limit, LimitMaximals,
    MeetNDualDP, Mux, Parallel, ParallelN, Series0,
    PlusValueDP, MeetNDP, JoinNDualDP, InvMult2Nat, MultValueDP,
    MinusValueDP, ProductNDP, Product2DP_U, Product2DP_L, ProductNNatDP, ProductNRcompDP,
    MinusValueRcompDP, MinusValueNatDP, InvMultValueNatDP, InvMultValueRcompDP,
    InvMultValueDP, SumNNatDP,
     SumNLDP, SumNUDP, Template, FuncNotMoreThan, RcompUnitsPowerDP, SquareNatDP)
from mcdp_dp.conversion import get_conversion
from mcdp_lang import parse_poset
from mcdp_posets import FiniteCollectionAsSpace, PosetProduct, Nat, Rcomp
from mocdp import MCDPConstants
from mcdp_dp.dp_max import MaxF1DP, MinR1DP, MaxR1DP, MinF1DP


all_primitivedps_tests = []
def add_as_test(f):
    all_primitivedps_tests.append(f)
    return f
    
@add_as_test
def ProductNDP_1():
    F1 = parse_poset('J')
    F2 = parse_poset('m')
    Fs = (F1, F2)
    R = parse_poset('J*m')
    return ProductNDP(Fs, R)

@add_as_test
def Product2DP_L_1():
    F1 = parse_poset('J')
    F2 = parse_poset('m')
    Fs = (F1, F2)
    R = parse_poset('J*m')
    return Product2DP_L(Fs, R, 5)

@add_as_test
def Product2DP_U_1():
    F1 = parse_poset('J')
    F2 = parse_poset('m')
    Fs = (F1, F2)
    R = parse_poset('J*m')
    return Product2DP_U(Fs, R, 5) # 

@add_as_test
def ProductNNatDP_2():
    return ProductNNatDP(2)

@add_as_test
def ProductNRcompDP_2():
    return ProductNRcompDP(2)

@add_as_test
def MinusValueDP1():
    F = parse_poset('J')
    U = parse_poset('mJ')
    v = 1000.0
    return MinusValueDP(F=F, c_value=v, c_space=U)    

@add_as_test
def MinusValueDP2():
    F = parse_poset('J')
    U = parse_poset('mJ')
    v = U.get_top()
    return MinusValueDP(F=F, c_value=v, c_space=U)    

@add_as_test
def MinusValueRcompDP1():
    v = 1000.0
    return MinusValueRcompDP(v)

@add_as_test
def MinusValueRcompDP2():
    U = Rcomp()
    v = U.get_top()
    return MinusValueRcompDP(v)

@add_as_test
def MinusValueNatDP1():
    v = 4
    return MinusValueNatDP(v)

@add_as_test
def MinusValueNatDP2():
    N = Nat()
    v = N.get_top()
    return MinusValueNatDP(v)

@add_as_test
def PlusValueDP1():
    F = parse_poset('J')
    U = parse_poset('mJ')
    v = 1000.0
    return PlusValueDP(F, c_value=v, c_space=U)


@add_as_test
def InvMultValueNatDP1zero():
    return InvMultValueNatDP(0)

@add_as_test
def InvMultValueNatDP2nonzero():
    return InvMultValueNatDP(2)

@add_as_test
def InvMultValueNatDP3top():
    return InvMultValueNatDP(Nat().get_top())

@add_as_test
def InvMultValueRcompDP1zero():
    return InvMultValueRcompDP(0.0)

@add_as_test
def InvMultValueRcompDP2nonzero():
    return InvMultValueRcompDP(10.0)

@add_as_test
def InvMultValueRcompDP3top():
    return InvMultValueRcompDP(Rcomp().get_top())

@add_as_test
def InvMultValueDP1zero():
    F = parse_poset('m*s')    
    U = parse_poset('s')
    R = parse_poset('m')
    v = 0.0
    return InvMultValueDP(F=F, R=R, unit=U, value=v)

@add_as_test
def InvMultValueDP2nonzero():
    F = parse_poset('m*s')    
    U = parse_poset('s')
    R = parse_poset('m')
    v = 10.0
    return InvMultValueDP(F=F, R=R, unit=U, value=v)

@add_as_test
def InvMultValueDP3top():
    F = parse_poset('m*s')    
    U = parse_poset('s')
    R = parse_poset('m')
    v = U.get_top()
    return InvMultValueDP(F=F, R=R, unit=U, value=v)

@add_as_test
def MultValueDP1nonzero():
    F = parse_poset('m')    
    U = parse_poset('s')
    v = 3.0
    R = parse_poset('m*s')
    return MultValueDP(F=F, R=R, unit=U, value=v)

@add_as_test
def MultValueDP2zero():
    F = parse_poset('m')    
    U = parse_poset('s')
    v = 0.0
    R = parse_poset('m*s')
    return MultValueDP(F=F, R=R, unit=U, value=v)

@add_as_test
def MultValueDP3top():
    F = parse_poset('m')    
    U = parse_poset('s')
    v = U.get_top()
    R = parse_poset('m*s')
    return MultValueDP(F=F, R=R, unit=U, value=v)

@add_as_test
def PlusValueRcompDP():
    from mcdp_dp import PlusValueRcompDP
    return PlusValueRcompDP(2.1)

@add_as_test
def PlusValueNatDP():
    from mcdp_dp import PlusValueNatDP
    return PlusValueNatDP(2)

@add_as_test
def CatalogueDP1():
    m1 = 'A'
    m2 = 'B'
    m3 = 'C'
    M = FiniteCollectionAsSpace([m1, m2, m3])
    F = parse_poset('V')
    R = parse_poset('J')
    
    entries = [
        (m1, 1.0, 2.0),
        (m2, 2.0, 4.0),
        (m3, 3.0, 6.0),
    ]
    return CatalogueDP(F, R, M, entries)

@add_as_test
def Constant1():
    R = parse_poset('V')
    value = 1.0
    return Constant(R, value)

@add_as_test
def ConstantMinimals1():
    R = parse_poset('V x V')
    values = [(1.0, 0.0), (0.5, 0.5)]
    return ConstantMinimals(R, values)

@add_as_test
def CoProductDP1():
    dps = (CatalogueDP1(), CatalogueDP1())
    return CoProductDP(dps)

# unfortunately we cannot test it like the others
# because it checks that the values are coherent
# def UncertainGate1():
#     F = parse_poset('Nat')
#     return UncertainGate(F)
# def UncertainGate_1():
#     F0 = parse_poset('Nat')
#     return UncertainGate(F0)

# def UncertainGateSym_1():
#     F0 = parse_poset('Nat')
#     return UncertainGateSym(F0)

@add_as_test
def CoProductDPLabels1():
    dp = CoProductDP1()
    labels = ['label1', 'label2']
    return CoProductDPLabels(dp, labels)

@add_as_test
def Mux1():
    """ a -> a """
    F = parse_poset('Nat')
    coords = ()
    return Mux(F, coords)

@add_as_test
def Mux2():
    """ <a> -> a """
    P0 = parse_poset('Nat')
    F = PosetProduct((P0,))
    coords = 0
    return Mux(F, coords)

@add_as_test
def Mux3():
    """ a -> <a> """
    F = parse_poset('Nat')
    coords = [()]
    return Mux(F, coords)

@add_as_test
def Mux4():
    """ <a, <b, c> > -> < <a, b>, c> """
    F = parse_poset('J x (m x Hz)')
    coords = [ [0, (1, 0)], (1,1)]
    return Mux(F, coords)

@add_as_test
def Mux5():
    """  One with a 1:

        <a, *> -> a
    """
    N = parse_poset('Nat')
    One = PosetProduct(())
    P = PosetProduct((N, One))
    coords = 0
    return Mux(P, coords)

 
@add_as_test
def Identity1():
    F = parse_poset('V')
    return Identity(F)

@add_as_test
def InvMult2Nat1():
    N = parse_poset('Nat')
    return InvMult2Nat(N, (N, N))

@add_as_test
def InvMult21():
    F = parse_poset('m')
    R1 = parse_poset('s')
    R2 = parse_poset('m/s')
    R = (R1, R2)
    return InvMult2(F, R)

@add_as_test
def InvMult2U1():
    F = parse_poset('m')
    R1 = parse_poset('s')
    R2 = parse_poset('m/s')
    R = (R1, R2)
    n = 8
    return InvMult2U(F, R, n)

@add_as_test
def InvMult2L1():
    F = parse_poset('m')
    R1 = parse_poset('s')
    R2 = parse_poset('m/s')
    R = (R1, R2)
    n = 8
    return InvMult2L(F, R, n)

@add_as_test
def InvPlus2Nat1():
    F = parse_poset('Nat')
    Rs = (F, F)
    return InvPlus2Nat(F, Rs)

@add_as_test
def InvPlus2_1():
    F = parse_poset('m')
    Rs = (F, F)
    return InvPlus2(F, Rs)

@add_as_test
def InvPlus2U_1():
    F = parse_poset('m')
    Rs = (F, F)
    n = 4
    return InvPlus2U(F, Rs, n)

@add_as_test
def InvPlus2L_1():
    F = parse_poset('m')
    Rs = (F, F)
    n = 9
    return InvPlus2L(F, Rs, n)

@add_as_test
def Limit_1():
    F = parse_poset('m')
    value = 5.0
    return Limit(F, value)

@add_as_test
def LimitMaximals_1():
    F = parse_poset('Nat x Nat')
    values = [(5, 1), (1, 5)]
    return LimitMaximals(F, values)

@add_as_test
def MaxR1DP_1():
    F = parse_poset('Nat')
    f = 4
    return MaxR1DP(F, f)

 
@add_as_test
def MinR1DP_1():
    F = parse_poset('Nat')
    f = 4
    return MinR1DP(F, f)

@add_as_test
def MaxF1DP_1():
    F = parse_poset('Nat')
    f = 4
    return MaxF1DP(F, f)

 
@add_as_test
def MinF1DP_1():
    F = parse_poset('Nat')
    f = 4
    return MinF1DP(F, f)


                   
@add_as_test
def Template_1():
    P = parse_poset('m')
    F = P
    R = PosetProduct((P,P))
    return Template(F, R)


@add_as_test
def DPLoop2_1():
    F1 = parse_poset('N')
    R1 = parse_poset('J')
    F2 = parse_poset('m')
    R2 = F2
    F = PosetProduct((F1, F2))
    R = PosetProduct((R1, R2))
    dp = Template(F, R)
    return DPLoop2(dp)

@add_as_test
def Parallel_1():
    dp1 = CatalogueDP1()
    dp2 = CatalogueDP1()
    return Parallel(dp1, dp2)

@add_as_test
def ParallelN_1():
    dps = (CatalogueDP1(), CatalogueDP1(),  CatalogueDP1())
    return ParallelN(dps)

@add_as_test
def Series0_1():
    dp1 = Constant1() # R = V
    V = parse_poset('V')
    dp2 = MaxR1DP(V, 2.0)
    return Series0(dp1, dp2)

# @add_as_test
# def Terminator_1():
#     F = parse_poset('Nat')
#     return Terminator(F)


@add_as_test
def JoinNDualDP_1():
    n = 3
    F0 = parse_poset('Nat')
    return JoinNDualDP(n, F0)

@add_as_test
def JoinNDP_1():
    n = 3
    F = parse_poset('Nat')
    return JoinNDP(n, F)

@add_as_test
def MeetNDualDP_1():
    n = 3
    P = parse_poset('Nat')
    return MeetNDualDP(n, P)
 
@add_as_test
def MeetNDP_1():
    n = 3
    P = parse_poset('Nat')
    return MeetNDP(n, P)

@add_as_test
def SumNLDP_1():
    m = parse_poset('m')
    Fs = (m, m)
    R = m
    nl = 5
    return SumNLDP(Fs=Fs,R=R,n=nl)

@add_as_test
def SumNUDP_1():
    m = parse_poset('m')
    Fs = (m, m)
    R = m
    nu = 5
    return SumNUDP(Fs=Fs,R=R,n=nu)

@add_as_test
def FuncNotMoreThan_1():
    F = parse_poset('m')
    limit = 2.0
    return FuncNotMoreThan(F, limit)
 
@add_as_test
def RcompUnitsPowerDP_1():
    F = parse_poset('m')
    num = 2
    den = 3
    return RcompUnitsPowerDP(F, num, den)

@add_as_test
def SquareNatDP_0():
    return SquareNatDP()

@add_as_test    
def SumNNatDP_2():
    return SumNNatDP(2)

@add_as_test
def Conversion_a():
    A = parse_poset('kg')
    B = parse_poset('g')
    return get_conversion(A, B)

if MCDPConstants.test_include_primitivedps_knownfailures:
    
    
    @add_as_test
    def SumNNatDP_3():
        return SumNNatDP(3)

#     @add_as_test
#     def DPLoop0_1():
#         F1 = parse_poset('N')
#         F2 = parse_poset('m')
#         R = F2
#         F = PosetProduct((F1, F2))
#         dp = Template(F, R)
#         return DPLoop0(dp)
#     
    @add_as_test
    def ProductNDP_3():
        F1 = parse_poset('J')
        F2 = parse_poset('m')
        F3 = parse_poset('s')
        Fs = (F1, F2, F3)
        R = parse_poset('J*m*s')
        return ProductNDP(Fs, R)
    
    @add_as_test
    def ProductNRcompDP_3():
        return ProductNRcompDP(3)
    
    @add_as_test
    def ProductNNatDP_3():
        return ProductNNatDP(3)
