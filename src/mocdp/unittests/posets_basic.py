from mocdp.unittests.generation import for_all_posets, for_some_posets
from mocdp.poset_utils import poset_check_chain


@for_all_posets
def check_poset1(_id_poset, poset):
    bot = poset.get_bottom()
    top = poset.get_top()
    poset.leq(bot, top)

@for_all_posets
def check_poset1_chain(_id_poset, poset):
    chain = poset.get_test_chain(n=5)
    poset_check_chain(poset, chain)

@for_some_posets('square')
def check_square(_id_poset, poset):
    P = poset

    assert P.get_bottom() == (0.0, 0.0)
    assert P.get_top() == (1.0, 1.0)


    assert P.leq((0.0, 0.0), (0.0, 0.5))
    assert not P.leq((0.0, 0.1), (0.0, 0.0))


