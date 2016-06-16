# -*- coding: utf-8 -*-
from .poset import Poset, NotLeq, NotBounded
from contracts import contract
from .space import Space, NotBelongs, NotEqual, Uninhabited
from mocdp.exceptions import do_extra_checks, mcdp_dev_warning
from contracts.utils import raise_desc
from mcdp_posets.poset import NotJoinable, NotMeetable
from networkx.algorithms.dag import descendants, ancestors

class FiniteCollectionAsSpace(Space):
    """ 
        This is a Space created out of a set of arbitrary hashable
        Python objects. 
    """

    def __init__(self, universe):
        self.elements = frozenset(universe)

    def belongs(self, x):
        return x in self.elements

    def check_equal(self, a, b):
        if a == b:
            pass
        else:
            raise NotEqual('%s ≠ %s' % (a, b))

    def check_leq(self, a, b):
        if a == b:
            pass
        else:
            raise_desc(NotLeq, 'Different', a=a, b=b)

    def format(self, x):
        return x.__repr__()

    def __repr__(self):
        return "FiniteCollectionAsSpace(%s)" % self.elements

mcdp_dev_warning('Join and Meet are not implemented')

class FinitePoset(FiniteCollectionAsSpace, Poset):

    @contract(universe='set')  # , relations='collection(tuple(*,*))')
    def __init__(self, universe, relations):
        FiniteCollectionAsSpace.__init__(self, universe)
        closure = transitive_closure(relations)
        # relations contains all closures, but not the cycles
        self.relations = frozenset(closure)

        self._find_top()
        self._find_bottom()

        #
        if do_extra_checks():
            for a, b in self.relations:
                assert a in universe
                assert b in universe

    def __eq__(self, b):
        if not isinstance(b, FinitePoset):
            return False
        same_elements = self.get_elements() == b.get_elements()
        same_relations = self.relations == b.relations
        return same_elements and same_relations

    def get_elements(self):
        return self.elements

    def __repr__(self):
        return "FinitePoset(%d els)" % len(self.elements)

    def get_test_chain(self, n):  # @UnusedVariable
        if not self.elements:
            raise Uninhabited()
        G = self._get_graph_closure_no_cycles()
        # this returns the paths at least of length 2
        from networkx.algorithms.dag import dag_longest_path

        path = list(dag_longest_path(G))
        if not path:
            one = list(self.elements)[0]
            return [one]
        assert path, (self.elements, self.relations)
        return path
        
    def _get_graph_closure_no_cycles(self):
        import networkx as nx
        G = nx.DiGraph()
        for a in self.elements:
            G.add_node(a)
        for a, b in self.relations:
            if a != b:
                G.add_edge(a, b)
        return G

    def _get_upper_closure(self, a):
        """ Returns a set of the upper closure of a """
        G = self._get_graph_closure_no_cycles()
        d = set(descendants(G, a))
        d.add(a)
        return d

    def _get_lower_closure(self, a):
        """ Returns a set of the upper closure of a """
        G = self._get_graph_closure_no_cycles()
        d = set(ancestors(G, a))
        d.add(a)
        return d

    def join(self, a, b):
        from mcdp_posets.find_poset_minima.baseline_n2 import poset_minima

        # find all descendants
        da = self._get_upper_closure(a)
        db = self._get_upper_closure(b)
        # take intersection
        inter = set(da) & set(db)
        if not inter:
            msg = 'There exists no join because upper closures separate.'
            raise_desc(NotJoinable, msg, a=self.format(a), b=self.format(b),
                       da=da, db=db)
        minima = poset_minima(inter, self.leq)
        if len(minima) > 1:
            msg = 'There exists no least element of intersection of upper closure.'
            raise_desc(NotJoinable, msg)
        return list(minima)[0]

    def meet(self, a, b):
        from mcdp_posets.find_poset_minima.baseline_n2 import poset_maxima

        # find all descendants
        da = self._get_lower_closure(a)
        db = self._get_lower_closure(b)
        # take intersection
        inter = set(da) & set(db)
        if not inter:
            msg = 'There exists no join because lower closures separate.'
            raise_desc(NotMeetable, msg, a=self.format(a), b=self.format(b),
                       da=da, db=db)
        maxima = poset_maxima(inter, self.leq)
        if len(maxima) > 1:
            msg = 'There exists no least element of intersection of lower closure.'
            raise_desc(NotMeetable, msg)
        return list(maxima)[0]

    def get_bottom(self):
        if self._bottom is None:
            raise NotBounded()
        else:
            return self._bottom

    def get_top(self):
        if self._top is None:
            raise NotBounded()
        else:
            return self._top

    def get_minimal_elements(self):
        from mcdp_posets.find_poset_minima.baseline_n2 import poset_minima
        minima = poset_minima(self.elements, self.leq)
        return minima

    def get_maximal_elements(self):
        geq = lambda a, b: self.leq(b, a)
        from mcdp_posets.find_poset_minima.baseline_n2 import poset_minima
        maxima = poset_minima(self.elements, geq)
        return maxima

    def _find_top(self):
        maxima = self.get_maximal_elements()
        if len(maxima) == 1:
            self._top = list(maxima)[0]
        else:
            self._top = None

    def _find_bottom(self):
        minima = self.get_minimal_elements()
        if len(minima) == 1:
            self._bottom = list(minima)[0]
        else:
            self._bottom = None

        
    def check_leq(self, a, b):
        if self.equal(a, b):
            return

        # XXX need to do the 
        if (a, b) in self.relations:
            return

        raise_desc(NotLeq, 'The two elements are not ordered',
                   a=self.format(a), b=self.format(b))

def transitive_closure(a):
    closure = set(a)
    while True:
        new_relations = set((x,w) for x,y in closure for q,w in closure if q == y)

        closure_until_now = closure | new_relations

        if closure_until_now == closure:
            break

        closure = closure_until_now

    return closure


class FiniteCollection():
    """ This is used as a value, whose Space is FinitecollectionsInclusion """
    @contract(elements='set|list', S=Space)
    def __init__(self, elements, S):
        self.elements = frozenset(elements)
        self.S = S

        if do_extra_checks():
            # XXX
            problems = []
            for m in elements:
                try:
                    self.S.belongs(m)
                except NotBelongs as e:
                    problems.append(e)
            if problems:
                msg = "Cannot create finite collection:\n"
                msg += "\n".join(str(p) for p in problems)
                raise NotBelongs(msg)

    def __repr__(self):  # ≤  ≥
        contents = ", ".join(self.S.format(m)
                        for m in sorted(self.elements))

        return "{%s}" % contents


class FiniteCollectionsInclusion(Poset):
    """ Lattice of finite collections 
    
        The bottom is the empty set.
        The top is the entire set.
    """

    @contract(S=Space)
    def __init__(self, S):
        self.S = S

# This can only be implemented if we can enumerate the elements of Space
#     def get_top(self):
#         return
#
    def get_bottom(self):
        return FiniteCollection(set([]), self.S)

    def __eq__(self, other):
        return isinstance(other, FiniteCollectionsInclusion) and self.S == other.S
#
#     def get_top(self):
#         x = self.P.get_top()
#         return UpperSet(set([x]), self.P)

#     def get_test_chain(self, n):
#         chain = self.P.get_test_chain(n)
#         f = lambda x: UpperSet(set([x]), self.P)
#         return map(f, chain)

    def belongs(self, x):
#         check_isinstance(x, UpperSet)
        if not isinstance(x, FiniteCollection):
            msg = 'Not a finite collection: %s' % x.__repr__()
            raise_desc(NotBelongs, msg, x=x)
        if not x.S == self.S:
            msg = 'Different spaces: %s ≠ %s' % (self.S, x.S)
            raise_desc(NotBelongs, msg, x=x)
        return True

    def check_equal(self, a, b):
        m1 = a.elements
        m2 = b.elements
        if not (m1 == m2):
            raise NotEqual('%s ≠ %s' % (m1, m2))

    def check_leq(self, a, b):
        e1 = a.elements
        e2 = b.elements
        res = e1.issubset(e2)
        if not res:
            msg = 'Not included'
            raise_desc(NotLeq, msg, e1=e1, e2=e2)

    def join(self, a, b):  # union
        elements = set()
        elements.update(a.elements)
        elements.update(b.elements)
        return FiniteCollection(elements, self.S)

    def format(self, x):
        contents = ", ".join(self.S.format(m)
                        for m in sorted(x.elements))

        return "{%s}" % contents

    def __repr__(self):
        return "set-of(%r)" % self.S
