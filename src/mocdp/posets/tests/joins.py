from mocdp.unittests.generation import for_all_posets

@for_all_posets
def check_poset_join(_id_poset, poset):
    P = poset
    chain = poset.get_test_chain(n=2)
    a = chain[0]
    b = chain[1]
    P.check_leq(a, b)

    j = P.join(a, b)
    m = P.meet(a, b)
    print('a = %s' % str(a))
    print('b = %s' % str(b))
    print('join = %s' % str(j))
    print('meet = %s' % str(m))
    P.check_equal(j, b)
    P.check_equal(m, a)



#
# @for_all_posets
# def check_poset_meet(_id_poset, poset):
#     P = poset
#     chain = poset.get_test_chain(n=2)
#     a = chain[0]
#     b = chain[1]
#     P.check_leq(a, b)


