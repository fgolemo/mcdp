#!/usr/bin/python
# -*- coding: utf-8 -*-
# $Id$
"""
GvGen - Generate dot file to be processed by graphviz
Copyright (c) 2012 Sebastien Tricaud <sebastien at honeynet org>

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, version 2 of the License.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
"""

from sys import stdout
from StringIO import StringIO

gvgen_version = "0.9.1"

debug = 0
debug_tree_unroll = 0

class GvGen():
    """
    Graphviz dot language Generation Class
    For example of usage, please see the __main__ function
    """

    def __init__(self, legend_name=None, options="compound=true;"): # allow links between clusters
        self.max_line_width = 10
        self.max_arrow_width = 2
        self.line_factor = 1
        self.arrow_factor = 0.5
        self.initial_line_width = 1.2
        self.initial_arrow_width = 0.8

        self.options = {}
        for option in options.split(";"):
            option = option.strip()
            if not option:
                continue
            key, value = option.split("=", 1)
            self.setOptions(**{key: value})

        self.__id = 0
        self.__nodes = []
        self.__links = []
        self.__browse_level = 0                  # Stupid depth level for self.browse
        self.__opened_braces = []                # We count opened clusters
        self.fd=stdout                           # File descriptor to output dot
        self.padding_str="   "                   # Left padding to make children and parent look nice
        self.__styles = {}
        self.__default_style = []
#         self.smart_mode = 0                      # Disabled by default

        # The graph has a legend
        if legend_name:
            self.setOptions(rankdir="LR")
            self.legend = self.newItem(legend_name)

    def setOptions(self, **options):
        for key, value in options.iteritems():
            self.options[key] = value

    def __node_new(self, name, parent=None, distinct=None):
        """
        Create a new node in the data structure
        @name: Name of the node, that will be the graphviz label
        @parent: The node parent
        @distinct: if true, will not create and node that has the same name

        Returns: The node created
        """

        # We first check for distincts
        if distinct:
            if self.__nodes:
                for e in self.__nodes:
                    props = e['properties']
                    if props['label'] == name:
                        # We found the label name matching, we return -1
                        return -1

        # We now insert into gvgen datastructure
        self.__id += 1
        node = {'id': self.__id,        # Internal ID
                'lock': 0,              # When the node is written, it is locked to avoid further references
                'parent': parent,       # Node parent for easy graphviz clusters
                'style':None,           # Style that GvGen allow you to create
                'properties': {         # Custom graphviz properties you can add, which will overide previously defined styles
                       'label': name
                       }
                }

        # Parents should be sorted first
        if parent:
                self.__nodes.insert(1, node)
        else:
                self.__nodes.append(node)

        return node

#     def __link_smart(self, link):
#         """
#         Creates a smart link if smart_mode activated:
#           if a -> b exists, and we now add a <- b,
#           instead of doing:  a -> b
#                                <-
#           we do: a <-> b
#         """

        # linkfrom = self.__link_exists(link['from_node'], link['to_node'])
        # linkto = self.__link_exists(link['to_node'], link['from_node'])

#         if self.smart_mode:
#             if linkto:
#                 self.__links.remove(linkto)
#                 self.propertyAppend(link, "dir", "both")
#
#             pw = self.propertyGet(linkfrom, "penwidth")
#             if pw:
#                 pw = float(pw)
#                 pw += self.line_factor
#                 if pw < self.max_line_width:
#                     self.propertyAppend(linkfrom, "penwidth", str(pw))
#             else:
#                 self.propertyAppend(link, "penwidth", str(self.initial_line_width))
#
#             aw = self.propertyGet(linkfrom, "arrowsize")
#             if aw:
#                 aw = float(aw)
#                 if aw < self.max_arrow_width:
#                     aw += self.arrow_factor
#                     self.propertyAppend(linkfrom, "arrowsize", str(aw))
#             else:
#                 self.propertyAppend(link, "arrowsize", str(self.initial_arrow_width))

        # if not linkfrom:
#         self.__links.append(link)


    def __link_new(self, from_node, to_node, label = None, cl_from_node=None, cl_to_node=None):
        """
        Creates a link between two nodes
        @from_node: The node the link comes from
        @to_node: The node the link goes to

        Returns: The link created
        """

        link = {'from_node': from_node,
                'to_node': to_node,
                'style':None,             # Style that GvGen allow you to create
                'properties': {},         # Custom graphviz properties you can add, which will overide previously defined styles
                'cl_from_node':None,      # When linking from a cluster, the link appears from this node
                'cl_to_node':None,        # When linking to a cluster, the link appears to go to this node
                }

        if label:
            link['properties']['label'] = label

        if cl_from_node:
            link['cl_from_node'] = cl_from_node
        if cl_to_node:
            link['cl_to_node'] = cl_to_node

        # We let smart link work for us
        # self.__link_smart(link)

        self.__links.append(link)

        return link

#     def __link_exists(self, from_node, to_node):
#         """
#         Find if a link exists
#         @from_node: The node the link comes from
#         @to_node: The node the link goes to
#
#         Returns: true if the given link already exists
#         """
#
#         for link in self.__links:
#             if link['from_node'] == from_node and link['to_node'] == to_node:
#                 return link
#
#         return None


    def __has_children(self, parent):
        """
        Find children to a given parent
        Returns the children list
        """
        children_list = []
        for e in self.__nodes:
            if e['parent'] == parent:
                children_list.append(e)

        return children_list

    def newItem(self, name, parent=None, distinct=None):
        node = self.__node_new(name, parent, distinct)

        return node

    def newLink(self, src, dst, label=None, cl_src=None, cl_dst=None):
        """
        Link two existing nodes with each other
        """

        return self.__link_new(src, dst, label, cl_src, cl_dst)

    def debug(self):
        for e in self.__nodes:
            print "element = " + str(e['id'])

    def collectLeaves(self, parent):
        """
        Collect every leaf sharing the same parent
        """
        cl = []
        for e in self.__nodes:
            if e['parent'] == parent:
                cl.append(e)

        return cl

    def collectUnlockedLeaves(self, parent):
        """
        Collect every leaf sharing the same parent
        unless it is locked
        """
        cl = []
        for e in self.__nodes:
            if e['parent'] == parent:
                if not e['lock']:
                    cl.append(e)

        return cl

    def lockNode(self, node):
        node['lock'] = 1

    #
    # Start: styles management
    #
    def styleAppend(self, stylename, key, val):
        if stylename not in self.__styles:
            self.__styles[stylename] = []

        self.__styles[stylename].append([key, val])

    def styleApply(self, stylename, node_or_link):
        node_or_link['style'] = stylename

    def styleDefaultAppend(self, key, val):
        self.__default_style.append([key, val])

    #
    # End: styles management
    #

    #
    # Start: properties management
    #
    def propertiesAsStringGet(self, node, props):
        """
        Get the properties string according to parent/children
        props is the properties dictionnary
        """
        allProps = {}

        #
        # Default style come first, they can then be overriden
        #
        if self.__default_style:
            allProps.update(self.__default_style)

        #
        # First, we build the styles
        #
        if node['style']:
            stylename = node['style']
            allProps.update(self.__styles[stylename])

        #
        # Now we build the properties:
        # remember they override styles
        #
        allProps.update(props)

        if self.__has_children(node):
            propStringList = ["%s=%s;\n" % (k, format_property(k, v)) for k, v in allProps.iteritems()]
            properties = ''.join(propStringList)
        else:
            if props:
                propStringList = ["%s=%s" % (k, format_property(k, v)) for k, v in allProps.iteritems()]
                properties = '[' + ','.join(propStringList) + ']'
            else:
                properties = ''

        return properties

    def propertiesLinkAsStringGet(self, link):
        props = {}

        if link['style']:
            stylename = link['style']

            # Build the properties string for node
            props.update(self.__styles[stylename])

        props.update(link['properties'])

        properties = ''
        if props:
            properties += ','.join(["%s=%s" % (str(k), format_property(k, val)) for k, val in props.iteritems()])
        return properties

    def propertyForeachLinksAppend(self, node, key, val):
        for l in self.__links:
            if l['from_node'] == node:
                props = l['properties']
                props[key] = val

    def propertyAppend(self, node_or_link, key, val):
        """
        Append a property to the wanted node or link
        mynode = newItem(\"blah\")
        Ex. propertyAppend(mynode, \"color\", \"red\")
        """
        props = node_or_link['properties']
        props[key] = val

    def propertyGet(self, node_or_link, key):
        """
        Get the value of a given property
        Ex. prop = propertyGet(node, \"color\")
        """
        try:
            props = node_or_link['properties']
            return props[key]
        except:
            return None

    def propertyRemove(self, node_or_link, key):
        """
        Remove a property to the wanted node or link
        mynode = newItem(\"blah\")
        Ex. propertyRemove(mynode, \"color\")
        """
        props = node_or_link['properties']
        del props[key]

    #
    # End: Properties management
    #

    #
    # For a good legend, the graph must have
    # rankdir=LR property set.
    #
    def legendAppend(self, legendstyle, legenddescr, labelin=None):
        if labelin:
            item = self.newItem(legenddescr, self.legend)
            self.styleApply(legendstyle, item)
        else:
            style = self.newItem("", self.legend)
            descr = self.newItem(legenddescr, self.legend)
            self.styleApply(legendstyle, style)
            link = self.newLink(style,descr)
            self.propertyAppend(link, "dir", "none")
            self.propertyAppend(link, "style", "invis")
            self.propertyAppend(descr,"shape","plaintext")

    def tree_debug(self, level, node, children):
        if children:
            print "(level:%d) Eid:%d has children (%s)" % (level,node['id'],str(children))
        else:
            print "Eid:"+str(node['id'])+" has no children"

    #
    # Core function that outputs the data structure tree into dot language
    #
    def tree(self, level, node, children):
        """
        Core function to output dot which sorts out parents and children
        and do it in the right order
        """
#         print('%stree(level %s, ID %s, %s)' % ('  ' * level, level, node['id'],
#                                                 len(children) if children else 'no children'))
        if debug:
            print "/* Grabed node = %s*/" % str(node['id'])

        if node['lock'] == 1:            # The node is locked, nothing should be printed
            if debug:
                print "/* The node (%s) is locked */" % str(node['id'])

            if self.__opened_braces:
                self.fd.write(level * self.padding_str)
                self.fd.write("}\n")
                self.__opened_braces.pop()
            return

        props = node['properties']

        if children:
            node['lock'] = 1
            self.fd.write(level * self.padding_str)

            # print('level %d Starting subcluster for %d %r' % (level, node['id'], node.get('label', '(no label)')))

            self.fd.write(self.padding_str + "subgraph cluster%d {\n" % node['id'])
            properties = self.propertiesAsStringGet(node, props)
            self.fd.write(level * self.padding_str)
            self.fd.write(self.padding_str + "%s" % properties)
            self.__opened_braces.append([node,level])
        else:
            # We grab appropriate properties
            properties = self.propertiesAsStringGet(node, props)
# "node%d %s;\n" % (node['id'], properties))
            # We get the latest opened elements
            if self.__opened_braces:
                last_cluster,last_level = self.__opened_braces[-1]
            else:
                last_cluster = None
                last_level = 0

            if debug:
                if node['parent']:
                    parent_str = str(node['parent']['id'])
                else:
                    parent_str = 'None'
                if last_cluster:
                    last_cluster_str = str(last_cluster['id'])
                else:
                    last_cluster_str = 'None'
                print "/* e[parent] = %s, last_cluster = %s, last_level = %d, opened_braces: %s */" % (parent_str, last_cluster_str,last_level,str(self.__opened_braces))

            # Write children/parent with properties
            if node['parent']:
                if node['parent'] != last_cluster:
                    while node['parent'] < last_cluster:
                        last_cluster,last_level =  self.__opened_braces[-1]
                        if  node['parent'] == last_cluster:
                            last_level += 1
                            # We browse any property to build a string
                            self.fd.write(last_level * self.padding_str)
                            self.fd.write(self.padding_str + "node%d %s;\n" % (node['id'], properties))
                            node['lock'] = 1
                        else:
                            self.fd.write(last_level * self.padding_str)
                            self.fd.write(self.padding_str + "}\n")
                            self.__opened_braces.pop()
                else:
                    self.fd.write(level * self.padding_str)
                    self.fd.write(self.padding_str + "node%d %s;\n" % (node['id'], properties) )
                    node['lock'] = 1
                    cl = self.collectUnlockedLeaves(node['parent'])
                    for l in cl:
                        props = l['properties']
                        properties = self.propertiesAsStringGet(l, props)
                        self.fd.write(last_level * self.padding_str)
                        self.fd.write(self.padding_str + self.padding_str + "node%d %s;\n" % (l['id'], properties))
                        node['lock'] = 1
                        self.lockNode(l)

                    self.fd.write(level * self.padding_str + "}\n")
                    self.__opened_braces.pop()

            else:
                self.fd.write(self.padding_str + "node%d %s;\n" % (node['id'], properties))
                node['lock'] = 1


    def browse(self, node, cb):
        """
        Browse nodes in a tree and calls cb providing node parameters
        """
        children = self.__has_children(node)
        if children:
            cb(self.__browse_level, node, str(children))
            for c in children:
                self.__browse_level += 1
                self.browse(c, cb)

        else:
            cb(self.__browse_level, node, None)
            self.__browse_level = 0

    def browse2_(self, G, id_node, cb, level):
        """
            cb(level, node_data, children_results)
        """
        children_result = {}
        children = G.successors(id_node)
        for c in children:
            rec = self.browse2_(G=G, id_node=c, cb=cb, level=level + 1)
            children_result[c] = rec
        node_data = G.node[id_node]['data']
        return cb(level, node_data, children_result)
    
    def browse2(self, cb):
        import networkx as nx
        G = nx.DiGraph()
        G.add_node('root', data=dict(id='root'))
        for n in self.__nodes:
            G.add_node(n['id'], data=n)
        
        for n in self.__nodes:
            parent = n['parent']
            if parent is None:
                id_parent = 'root'
            else:
                id_parent = parent['id']
            G.add_edge(id_parent, n['id'])

        return self.browse2_(G=G, id_node='root', cb=cb, level=0)

    def structure(self):
        def example(level, node, children_results):  # @UnusedVariable
            if children_results:
                c = ", ".join(["%s" % (v) for k, v in children_results.items()])  # @UnusedVariable
                return "%s { %s } " % (node['id'], c)
            else:
                return node['id']
        return self.browse2(example)

    def dot2(self):
        from contracts.utils import indent
        def indented_results(children_results):
            s = ""
            for cs in children_results.values():
                s += indentu(cs, '   ') + '\n'
            return s

        def render_dot_root(level, node, children_results):  # @UnusedVariable
            s = "digraph G { \n"
            if self.options:
                for key, value in self.options.iteritems():
                    s += ("    %s=%s;" % (key, value))
                s += ("\n")
            assert isinstance(s, str), s.__repr__()
            r = indented_results(children_results)  # .decode("unicode_escape")
            try:
                s += r
            except UnicodeDecodeError:
                # print r[210:220].__repr__()
#                 print type(r), type(s)
#                 print r[1200:1230].__repr__()
#                 print r.__repr__()
                raise

            self.fd = StringIO()
            for n in self.__nodes:            
                self.dotLinks(n)

            s += indent(self.fd.getvalue(), '   ')
            s += '}'
            return s

        def render_dot_subgraph(level, node, children_results):  # @UnusedVariable
            s = "subgraph cluster%d { \n" % node['id']
            properties = self.propertiesAsStringGet(node, node['properties'])
            s += indent('   ', properties)
            s += indented_results(children_results)
            s += '}'
            return s

        def render_dot_node(level, node, children_results):  # @UnusedVariable
            properties = self.propertiesAsStringGet(node, node['properties'])
            return "node%d %s;\n" % (node['id'], properties)

        def render_dot(level, node, children_results):  # @UnusedVariable
            
            if node['id'] == 'root':
                return render_dot_root(level, node, children_results)
            
            if children_results:
                return render_dot_subgraph(level, node, children_results)
            else:
                return render_dot_node(level, node, children_results)

        return self.browse2(render_dot)

    def dotLinks(self, node):
        """
        Write links between nodes
        """
        for l in self.__links:
            if l['from_node'] == node:
                # Check if we link form a cluster
                children = self.__has_children(node)
                if children:
                    if l['cl_from_node']:
                        src = l['cl_from_node']['id']
                    else:
                        src = children[0]['id']
                    cluster_src = node['id']
                else:
                    src = node['id']
                    cluster_src = ''

                # Check if we link to a cluster
                children = self.__has_children(l['to_node'])
                if children:
                    if l['cl_to_node']:
                        dst = l['cl_to_node']['id']
                    else:
                        dst = children[0]['id']
                    cluster_dst = l['to_node']['id']
                else:
                    dst = l['to_node']['id']
                    cluster_dst = ''

                self.fd.write("node%d->node%d" % (src, dst))

                props = self.propertiesLinkAsStringGet(l)

                # Build new properties if we link from or to a cluster
                if cluster_src:
                    if props:
                        props += ','
                    props += "ltail=cluster%d" % cluster_src
                if cluster_dst:
                    if props:
                        props += ','
                    props += "lhead=cluster%d" % cluster_dst

                if props:
                    self.fd.write(" [%s]" % props)

                self.fd.write(";\n")

    def dot(self, fd=stdout):
        """
        Translates the datastructure into dot
        """
        try:
            self.fd = fd

            self.fd.write("/* Generated by GvGen v.%s (http://www.picviz.com/sections/opensource/gvgen.html) */\n\n" % (gvgen_version))

            self.fd.write("digraph G {\n")

            if self.options:
                for key, value in self.options.iteritems():
                    self.fd.write("%s=%s;" % (key, value))
                self.fd.write("\n")

            # We write parents and children in order
            for e in self.__nodes:
                if debug_tree_unroll:
                        self.browse(e, self.tree_debug)
                else:
                        self.browse(e, self.tree)

            # We write the connection between nodes
            for e in self.__nodes:
                self.dotLinks(e)

            # We put all the nodes belonging to the parent
            self.fd.write("}\n")
        finally:
            # Remove our reference to file descriptor
            self.fd = None

    # XXX: unused
    # def remove_identity_nodes(self):
    #     """
    #         Certainly need to remove ADD_ORDER = True
            
    #     """
    #     def is_identity(n):
    #         return n['properties']['label'] == 'Identity'

    #     import networkx as nx
    #     G = nx.DiGraph()

    #     leqs = set()
    #     identities = set()
    #     for n in self.__nodes:
    #         if is_identity(n):
    #             identities.add(n['id'])
    #         if n['style'] == 'leq':
    #             leqs.add(n['id'])

    #     for l in self.__links:
    #         from_node = l['from_node']['id']
    #         to_node = l['to_node']['id']
    #         G.add_edge(from_node, to_node)

    #     def remove_link(tail , head):
    #         def matches(l):
    #             return (l['to_node']['id'] == head) and(l['from_node']['id'] == tail)
    #         links = []
    #         nmatches = 0
    #         for l in self.__links:
    #             if not matches(l):
    #                 links.append(l)
    #                 print l['from_node']['id'], l['to_node']['id']
    #             else:
    #                 nmatches += 1
    #         if not nmatches:
    #             raise ValueError('No link %s - %s found' % (tail, head))
    #         self.__links = links

    #     def remove_node(n):
    #         def matches(x):
    #             return x['id'] == n
    #         self.__nodes = [x for x in self.__nodes if not matches(x)]

    #         for l in self.__links:
    #             if l['to_node']['id'] == n:
    #                 raise ValueError('Found link to node %r' % n)
    #             if l['from_node']['id'] == n:
    #                 raise ValueError('Found link from node %r' % n)

    #     def get_node(n):
    #         for x in self.__nodes:
    #             if x['id'] == n:
    #                 return x

    #     def sub_link_from(old, new):
    #         for l in self.__links:
    #             if l['from_node']['id'] == old:
    #                 l['from_node'] = get_node(new)



    #     # look for A -l1--> [prev_leq] -l2-> [Identity n] --l3-> [B]
    #     # look for A -l3--> [B]
    #     for n in identities:
    #         pred = G.predecessors(n)
    #         has_prev_leq = len(pred) == 1 and pred[0] in leqs
    #         succ = G.successors(n)
    #         has_one_succ = len(succ) == 1
    #         has_prev_leq_one = has_prev_leq and len(G.predecessors(pred[0])) == 1

    #         if not has_prev_leq_one or not has_one_succ:
    #             print('This one is not eligible (prev_eq')
    #             continue

    #         prev_leq = pred[0]
    #         A = G.predecessors(prev_leq)[0]

    #         # we also want the previous ones to be

    #         remove_link(A, prev_leq)  # l1
    #         remove_link(prev_leq, n)  # l2
    #         sub_link_from(old=n, new=A)

    #         print 'n', n, 'pred', pred, 'succ', succ
    #         remove_node(n)
    #         remove_node(prev_leq)



#         self.__links = []


def format_property(k, v):  # @UnusedVariable
    s = str(v)
    def escape(x):
        return x.replace('\n', '\\n')
    if s and s[0] == '<':
        res = '<%s>' % escape(s)
    else:
        res = '"%s"' % escape(s)
    return res

if __name__ == "__main__":
    graph = GvGen()

    graph.smart_mode = 1

    graph.styleDefaultAppend("color","blue")

    parents = graph.newItem("Parents")
    father = graph.newItem("Bob", parents)
    mother = graph.newItem("Alice", parents)
    children = graph.newItem("Children")
    child1 = graph.newItem("Carol", children)
    child2 = graph.newItem("Eve", children)
    child3 = graph.newItem("Isaac", children)
    postman = graph.newItem("Postman")
    graph.newLink(father,child1)
    graph.newLink(child1, father)
    graph.newLink(father, child1)
    graph.newLink(father,child2)
    graph.newLink(mother,child2)
    myl = graph.newLink(mother,child1)
    graph.newLink(mother,child3)
    graph.newLink(postman,child3,"Email is safer")
    graph.newLink(parents, postman)    # Cluster link

    graph.propertyForeachLinksAppend(parents, "color", "blue")

    graph.propertyForeachLinksAppend(father, "label", "My big link")
    graph.propertyForeachLinksAppend(father, "color", "red")

    graph.propertyAppend(postman, "color", "red")
    graph.propertyAppend(postman, "fontcolor", "white")

    graph.styleAppend("link", "label", "mylink")
    graph.styleAppend("link", "color", "green")
    graph.styleApply("link", myl)
    graph.propertyAppend(myl, "arrowhead", "empty")

    graph.styleAppend("Post", "color", "blue")
    graph.styleAppend("Post", "style", "filled")
    graph.styleAppend("Post", "shape", "rectangle")
    graph.styleApply("Post", postman)


    graph.dot()


def indentu(s, prefix, first=None):
    assert isinstance(prefix, str)
    lines = s.split('\n')
    if not lines: return ''

    if first is None:
        first = prefix

    m = max(len(prefix), len(first))

    prefix = ' ' * (m - len(prefix)) + prefix
    first = ' ' * (m - len(first)) + first

    # differnet first prefix
    res = ['%s%s' % (prefix, line.rstrip()) for line in lines]
    res[0] = '%s%s' % (first, lines[0].rstrip())
    return '\n'.join(res)
