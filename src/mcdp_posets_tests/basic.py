import itertools

from comptests.registrar import comptest
from contracts.utils import raise_desc
from mcdp_posets import FinitePoset
from mcdp_posets import Interval, NotBounded, PosetProduct, Uninhabited, NotBelongs, NotEqual, Rcomp
from mcdp_posets import Nat
from mcdp_posets import PosetCoproduct, PosetCoproductWithLabels
from mcdp_posets import NotLeq
from mcdp_posets.utils import poset_check_chain, check_minimal, check_maximal
from mcdp_tests.generation import for_all_posets
import numpy as np
from mcdp_posets.multiset import Multisets


@for_all_posets
def check_poset1(_id_poset, poset):
    """ Checks that bottom <= top """
    try:
        bot = poset.get_bottom()
    except NotBounded:
        return

    poset.leq(bot, bot)
    
    poset.format(bot)
    
    x = poset.witness()
    poset.leq(bot, x)

    try:
        top = poset.get_top()
    except NotBounded:
        pass
    else:
        poset.leq(top, top)
        poset.leq(bot, top)
    
        poset.leq(x, top)
        poset.format(top)

@for_all_posets
def check_poset1_chain(id_poset, poset):
    try:
        #from mcdp_posets import poset_check_chain
        chain = poset.get_test_chain(n=5)
        poset_check_chain(poset, chain)
    except Uninhabited:
        # list exceptions that can be empty
        if isinstance(poset, FinitePoset):
            return
        raise Exception('%s %s is Uninhabited' % (id_poset, poset))
        

    for a in chain:
        poset.check_equal(a, a)
        m = poset.meet(a, a)
        poset.check_equal(m, a)
        m = poset.join(a, a )
        poset.check_equal(a, a)

    for a, b in itertools.combinations(chain, 2):
        try:
            poset.check_equal(a, b)
        except NotEqual:
            pass
        else:
            raise_desc(Exception, 'failed', a=a, b=b, poset=poset, chain=chain)

    for i, j in itertools.combinations(range(len(chain)), 2):
        if i > j:
            i, j = j, i
        
        e1 = chain[i]
        e2 = chain[j]
        
        print('Comparing e1 = {} and e2 = {}'.format(poset.format(e1), poset.format(e2)))
        
        poset.check_leq(e1, e2)
        try: 
            poset.check_leq(e2, e1)
        except NotLeq:
            pass
        
        meet1 = poset.meet(e1, e2)
        meet2 = poset.meet(e2, e1)
        
        print('meet1: {}'.format(meet1))
        print('meet2: {}'.format(meet2))

        join1 = poset.join(e1, e2)
        join2 = poset.join(e2, e1)

        print('join1: {}'.format(join1))
        print('join2: {}'.format(join2))
        
        poset.check_equal(meet1, e1)
        poset.check_equal(meet2, e1)
        poset.check_equal(join1, e2)
        poset.check_equal(join2, e2)

        


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
    print('top: {}'.format(poset.format(top)))
    poset.check_leq(top, top)
    a = poset.witness()
    print('a: {}'.format(poset.format(a)))
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
    P = PosetCoproductWithLabels(subs, labels=('one', 'two'))
    return P

def test_Multiset_1():
    P0 = FinitePoset(['a','b','c'], [])
    P = Multisets(P0)
    return P

def test_Multiset_2():
    P0 = Rcomp()
    P = Multisets(P0)
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
        
@for_all_posets
def check_minimal_elements(_, poset):
    try:
        poset.get_minimal_elements()
    except NotBounded:
        pass

@for_all_posets
def check_maximal_elements(_, poset):
    try:
        poset.get_maximal_elements()
    except NotBounded:
        pass
    
    
