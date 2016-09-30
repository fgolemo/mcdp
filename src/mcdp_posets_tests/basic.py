import itertools

from comptests.registrar import comptest
from contracts.utils import raise_desc
from mcdp_posets import Interval, NotBounded, PosetProduct, Uninhabited, NotBelongs, NotEqual, Rcomp
from mcdp_tests.generation import for_all_posets
import numpy as np
from mcdp_posets.poset_coproduct import PosetCoproduct, PosetCoproductWithLabels
from mcdp_posets.finite_poset import FinitePoset
from mcdp_posets.utils import poset_check_chain, check_minimal, check_maximal
from mcdp_posets.nat import Nat


@for_all_posets
def check_poset1(_id_poset, poset):
    """ Checks that bottom <= top """
    try:
        bot = poset.get_bottom()
    except NotBounded:
        return

    poset.leq(bot, bot)

    try:
        top = poset.get_top()
    except NotBounded:
        pass
    else:
        poset.leq(bot, top)

@for_all_posets
def check_poset1_chain(_id_poset, poset):
    try:
        from mcdp_posets import poset_check_chain

        chain = poset.get_test_chain(n=5)
        poset_check_chain(poset, chain)

    except Uninhabited:
        pass

    for a in chain:
        poset.check_equal(a, a)
        
    for a, b in itertools.combinations(chain, 2):
        try:
            poset.check_equal(a, b)
        except NotEqual:
            pass
        else:
            raise_desc(Exception, 'failed', a=a, b=b, poset=poset)


@for_all_posets
def check_poset_witness(_id_poset, poset):
    try:
        poset.witness()
    except Uninhabited:
        pass


@for_all_posets
def check_poset_top(_id_poset, poset):
    try:
        top = poset.get_top()
    except NotBounded:
        return
    
    poset.check_leq(top, top)
    a = poset.witness()
    poset.check_leq(a, top)
    


@for_all_posets
def check_poset_bottom(_id_poset, poset):
    try:
        bottom = poset.get_bottom()
    except NotBounded:
        return
    
    poset.check_leq(bottom, bottom)
    a = poset.witness()
    poset.check_leq(bottom, a)
    
class Stranger():
    pass

@for_all_posets
def check_poset_not_belongs(_id_poset, poset):
    try:
        poset.belongs(Stranger())
    except NotBelongs:
        pass
    else:
        raise Exception()
    
@comptest
def check_square():
    I = Interval(0.0, 1.0)
    P = PosetProduct((I, I))

    assert P.get_bottom() == (0.0, 0.0)
    assert P.get_top() == (1.0, 1.0)

    assert P.leq((0.0, 0.0), (0.0, 0.5))
    assert not P.leq((0.0, 0.1), (0.0, 0.0))


@comptest
def check_equality():
    assert Rcomp() == Rcomp()
    assert not (Rcomp() != Rcomp())
    
    
@comptest
def check_rcomp_corner_cases():
    P = Rcomp()
    def not_belongs(x):
        try:
            P.belongs(x)
        except NotBelongs:
            pass
        else:
            raise Exception('Violation with {}'.format(x))
     
    not_belongs(2) # not a float
    not_belongs(-2.0) # negative
    not_belongs(np.inf)
    not_belongs(np.nan)  
      
@comptest
def check_coproduct():
    try:
        PosetCoproduct(())
    except ValueError:
        pass
    else:
        assert False

def test_PosetCoproductWithLabels_1(): 
    # used in coprod1.mcdp_poset
    f1 = FinitePoset(['a','b','c'], [])
    f2 = FinitePoset(['A','B','C'], [])
    subs = (f1, f2)
    P = PosetCoproductWithLabels(subs)
    return P

@comptest
def check_posets_misc1():
    try:
        poset_check_chain(Nat(), [2, 1])
    except ValueError:
        pass
    else:
        assert False

    try:
        check_minimal([2, 1], Nat())
    except ValueError:
        pass
    else:
        assert False

    try:
        check_maximal([2, 1], Nat())
    except ValueError:
        pass
    else:
        assert False
