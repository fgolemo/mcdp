from contracts import contract
from mcdp_dp.dp_flatten import MuxMap
from mcdp_posets.poset_product import PosetProduct
from mcdp_posets.types_universe import (express_value_in_isomorphic_space,
    get_types_universe)
from mcdp_posets.uppersets import UpperSet, UpperSets, upperset_project_map
import itertools
from mcdp_posets.space import Space
_ = Space

@contract(ua=UpperSet, ub=UpperSet)
def less_resources2(ua, ub):
    """
    
        ua must be <= ub
    """
    Pa = ua.P
    Pb = ub.P

    if not isinstance(Pa, PosetProduct) or not isinstance(Pb, PosetProduct):
        raise NotImplementedError((Pa, Pb))

    tu = get_types_universe()

    matches = []
    for i, P in enumerate(Pa.subs):
        for j, Q in enumerate(Pb.subs):
            if j in matches: continue
            if tu.leq(P, Q):
                matches.append(j)
                break
        else:
            # msg = 'Could not find match.'
            return False

    # now we have found an embedding

    # first we create a projection for Pb
    m1 = MuxMap(F=Pb, coords=matches)

    ub2 = upperset_project_map(ub, m1)
    Pb2 = ub2.P
    UPb2 = UpperSets(Pb2)

    # now we create the embedding
    A_to_B, _ = tu.get_embedding(Pa, Pb2)
    ua2 = upperset_project_map(ua, A_to_B)

    print('Pa: %s' % Pa)
    print('Pb2:  %s' % Pb2)
    print('ua2: %s' % ua2)
    print('ub2: %s' % ub2)

    return UPb2.leq(ua2, ub2)



class CompareDifferentResources():

    @contract(ua=UpperSet, ub=UpperSet)
    def less_resources(self, ua, ub):
        """ 
            Returns True if ua uses less resources than ub.
        
            This only works for PosetProducts 
        """
        U, a, b = get_common(ua, ub)
        return U.leq(a, b)

@contract(ua=UpperSet, ub=UpperSet, returns='tuple($Space, $UpperSet, $UpperSet)')
def get_common(ua, ub):
    Pa = ua.P
    Pb = ub.P

    if not isinstance(Pa, PosetProduct) or not isinstance(Pb, PosetProduct):
        raise NotImplementedError((Pa, Pb))

    # first, it might be that they have different spaces

    # let's find out how to match them

    tu = get_types_universe()
    # for each i in Pa, we will match it to the first
    matches1 = []
    for i, P in enumerate(Pa.subs):
        for j, Q in enumerate(Pb.subs):
            if ('B', j) in matches1: continue
            if tu.leq(P, Q):
                matches1.append(('B', j))
                break
        else:
            matches1.append(('A', i))
    matches2 = []
    for j, Q in enumerate(Pb.subs):
        if ('B', j) in matches1:
            # used by somebody
            matches2.append(('B', j))
        else:
            for i, P in enumerate(Pa.subs):
                if matches1[i] is not None: continue
                if tu.leq(Q, P):
                    matches2.append(('A', i))
                    break
            else:
                matches2.append(('B', j))

    print('matches1:  %s' % matches1)
    print('matches2: %s' % matches2)

    used = sorted(set(matches1 + matches2))
    def get_P(_):
        (which, index) = _
        if which == 'A': return Pa.subs[index]
        if which == 'B': return Pb.subs[index]
        assert False

    Ps = PosetProduct(tuple(map(get_P, used)))
    print('used: %s' % used)
    print('Ps: %s' % Ps)

    # now we need to complete the first
    Ps_a = get(matches1, used, Ps, get_P, Pa, ua)
    Ps_b = get(matches2, used, Ps, get_P, Pb, ub)

    print('Ps_a: %s' % Ps_a)
    print('Ps_b: %s' % Ps_b)

    S = UpperSets(Ps)
    return S, Ps_a, Ps_b


def get(matches, used, Ps, get_P, Pa, ua):
    others = list(set(used) - set(matches))
    extra = PosetProduct(tuple(map(get_P, others)))
    print('extra for Pa: %s' % extra)
    Pa_comp = PosetProduct(Pa.subs + extra.subs)
    print('Pa_comp: %s' % Pa_comp)
    extra_minimals = extra.get_minimal_elements()
    m_matches = matches + others
    s = set()
    R = set()
    for m1, m2 in itertools.product(ua.minimals, extra_minimals):
        m = m1 + m2
        s.add(m)
        r = [None] * len(used)
        for i, a in enumerate(used):
            S1 = Pa_comp.subs[m_matches.index(a)]
            s1 = m[m_matches.index(a)]
            S2 = get_P(a)
            r[i] = express_value_in_isomorphic_space(S1, s1, S2)
        r = tuple(r)
        R.add(r)
    Pa_comp_lb = Pa_comp.Us(s)
    print('Pa_comp_lb: %s' % Pa_comp_lb)
    Ps_a = Ps.Us(R)
    return Ps_a

#
# class P_to_join():
#
#     def __init__(self, P1, P_join, matches):
#         """ Ps: the join """
#         self.P1 = P1
#         self.P_join = P_join
#         self.used = matches
#
#     def __call__(self, lb):
#         assert isinstance(lb, UpperSet)
        

