from mocdp.unittests.generation import for_all_posets
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

def test_1():

    from mocdp.dp_bat import BatteryDP
    battery = BatteryDP()

    res = battery.solve(0.0)
    res = battery.solve(1.0)
