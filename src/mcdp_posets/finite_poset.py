# -*- coding: utf-8 -*-
from contracts import contract
from contracts.utils import raise_desc, check_isinstance
from networkx.algorithms.dag import ancestors, descendants, dag_longest_path

from mcdp.development import do_extra_checks

from .finite_collection_as_space import FiniteCollectionAsSpace
from .poset import NotBounded, NotJoinable, NotLeq, NotMeetable, Poset
from .space import Uninhabited


__all__ = [
    'FinitePoset',
] 

class FinitePoset(FiniteCollectionAsSpace, Poset):

    @contract(universe='set')  # , relations='collection(tuple(*,*))')
    def __init__(self, universe, relations):
        check_isinstance(universe, set)
        FiniteCollectionAsSpace.__init__(self, universe)
        closure = transitive_closure(relations)
        # relations contains all closures, but not the cycles
        self.relations = frozenset(closure)

        self._find_top()
        self._find_bottom()

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
        if len(self.elements) <= 5:
            return self.repr_long()
        else:
            return "FinitePoset(%d els)" % len(self.elements)

    def repr_long(self):
        return ('FinitePoset(%d el = %s)' % (len(self.elements), 
                                             list(self.elements).__repr__()))

    def get_test_chain(self, n):  # @UnusedVariable
        if not self.elements:
            raise Uninhabited()
        G = self._get_graph_closure_no_cycles()
        # this returns the paths at least of length 2
        

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

    def leq(self, a, b):
        if self.equal(a, b):
            return True
        if (a, b) in self.relations:
            return True
        return False

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

