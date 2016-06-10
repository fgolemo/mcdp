from mocdp.unittests.generation import for_all_posets, for_some_posets
from comptests.registrar import comptest
from mcdp_posets.poset import NotBounded
from mcdp_posets.space import Uninhabited


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

@for_some_posets('square')
def check_square(_id_poset, poset):
    P = poset

    assert P.get_bottom() == (0.0, 0.0)
    assert P.get_top() == (1.0, 1.0)

    assert P.leq((0.0, 0.0), (0.0, 0.5))
    assert not P.leq((0.0, 0.1), (0.0, 0.0))


@comptest
def check_equality():
    from mcdp_posets.rcomp import Rcomp
    assert Rcomp() == Rcomp()
    assert not (Rcomp() != Rcomp())
