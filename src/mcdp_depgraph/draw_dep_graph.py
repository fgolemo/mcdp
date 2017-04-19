# -*- coding: utf-8 -*-
from mcdp_report import my_gvgen
from mcdp_report.gg_utils import gg_figure
from mcdp_utils_misc.memoize_simple_imp import memoize_simple
from reprep import Report

from .find_dep import FindDependencies


def draw_libdepgraph(res):
    """ Just display the dependencies between libraries """
    r = Report()
    fd = res['fd']
    assert isinstance(fd, FindDependencies)

    G = fd.create_libgraph()
    # create another graph only with libraries
    
    gg = my_gvgen.GvGen(options="rankdir=TB")

    @memoize_simple
    def get_gg_node(entry):
        label = entry
        return gg.newItem(label)

    for entry in G.nodes():
        get_gg_node(entry)

    for entry1, entry2 in G.edges():
        n1 = get_gg_node(entry1)
        n2 = get_gg_node(entry2)
        gg.newLink(n1, n2)

    gg_figure(r, 'graph', gg, do_dot=False)

    return r

    

def draw_depgraph(res):
    r = Report()
    fd = res['fd']
    assert isinstance(fd, FindDependencies)

    G = fd.create_graph()

    gg = my_gvgen.GvGen(options="rankdir=TB")

    @memoize_simple
    def get_gg_cluster(libname):
        print('creating cluster %s ' % entry)
        return gg.newItem(libname)

    @memoize_simple
    def get_gg_node(entry):
        print('creating node %s ' % entry)
        parent = get_gg_cluster(entry.libname)
        label = '%s/%s' % (entry.libname, entry.name)
        return gg.newItem(label, parent=parent)

    for entry in G.nodes():
        get_gg_node(entry)

    for entry1, entry2 in G.edges():
        n1 = get_gg_node(entry1)
        n2 = get_gg_node(entry2)
        gg.newLink(n1, n2)

    gg_figure(r, 'graph', gg, do_dot=False)

    return r
