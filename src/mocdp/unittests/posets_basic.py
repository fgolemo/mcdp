from mocdp.unittests.generation import for_all_posets


@for_all_posets
def check_poset1(_id_poset, poset):
    bot = poset.get_bottom()
    top = poset.get_top()
    poset.leq(bot, top)
    

def test_1():

    battery = BatteryDP()

    res = battery.solve(0.0)
    res = battery.solve(1.0)
