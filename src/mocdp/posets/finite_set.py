# -*- coding: utf-8 -*-
from mocdp.posets.poset import Poset, NotLeq, NotBounded
from contracts import contract
from mocdp.posets.space import Space, NotBelongs, NotEqual, Uninhabited
from mocdp.exceptions import do_extra_checks, mcdp_dev_warning
from contracts.utils import raise_desc

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
    @contract(universe='set', relations='seq(tuple(*,*))')
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

    def join(self, a, b):
        raise NotImplementedError()

    def meet(self, a, b):
        raise NotImplementedError()

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

    def _get_minimal_elements(self):
        from mocdp.posets.find_poset_minima.baseline_n2 import poset_minima
        minima = poset_minima(self.elements, self.leq)
        return minima

    def _get_maximal_elements(self):
        geq = lambda a, b: self.leq(b, a)
        from mocdp.posets.find_poset_minima.baseline_n2 import poset_minima
        maxima = poset_minima(self.elements, geq)
        return maxima

    def _find_top(self):
        maxima = self._get_maximal_elements()
        if len(maxima) == 1:
            self._top = list(maxima)[0]
        else:
            self._top = None

    def _find_bottom(self):
        minima = self._get_minimal_elements()
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
