from __future__ import absolute_import, print_function, division, unicode_literals
import networkx as nx
from collections import deque


class TreeGraph(object):
    root_name = 'root'

    def __init__(self, separator='/'):
        self.separator = separator
        self.graph = nx.DiGraph()
        self.graph.add_node(self.root_name)

    def _validate_path(self, path):
        if path[0] != self.separator:
            raise ValueError('Path must start with {}'.format(self.separator))
        if path[-1] == self.separator:
            raise ValueError('Path must not end with {}'.format(self.separator))

    def _root_path(self, path):
        return '{}{}'.format(self.root_name, path or '')

    def _deroot_path(self, path):
        return path[len(self.root_name):]

    def add(self, path):
        self._validate_path(path)
        path = self._root_path(path)

        # TODO: optimise this to not continually add nodes
        segments = path.split(self.separator)
        for index in range(len(segments)):
            previous = self.separator.join(segments[:index])
            current = self.separator.join(segments[:index + 1])

            # create node
            if current not in self.graph.nodes():
                self.graph.add_node(current)

                # connect to parent
                if previous:
                    self.graph.add_edge(previous, current)

            # if we're at the endge
            if current == path:
                node = self.graph.node[current]
                edge = self.graph[previous][current]
                return edge, node

    def remove(self, path):
        self._validate_path(path)
        #path = self._root_path(path)

        # remove this node and all below it
        #for node in nx.bfs_tree(self.graph, path):
        for node in self.dfs(path):
            node = self._root_path(node)
            self.graph.remove_node(node)

    def parent(self, path):
        self._validate_path(path)
        parent = self.separator.join(path.split(self.separator)[:-1])
        if not parent:
            parent = None
        return parent

    def node(self, path):
        self._validate_path(path)
        path = self._root_path(path)
        return self.graph.node[path]

    def edge(self, src, dst):
        self._validate_path(src)
        src = self._root_path(src)
        self._validate_path(dst)
        dst = self._root_path(dst)
        return self.graph.edge[src][dst]

    def nodes(self, data=False):
        nodes = set(self.graph.nodes(data))
        # remove root
        nodes.remove(self.root_name)
        # remove root/ from paths
        nodes = map(lambda x: self._deroot_path(x), nodes)
        return nodes

    def edges(self, data=False):
        edges = self.graph.edges(data)
        # remove root edges
        edges = filter(lambda x: x[0] != self.root_name, edges)
        return edges

    def parent_edge(self, path):
        parent = self.parent(path)
        parent = self._root_path(parent)
        path = self._root_path(path)
        return self.graph.edge[parent][path]

    def dfs(self, path=None):
        if path:
            self._validate_path(path)
        path = self._root_path(path)

        # pop the next node in the queue
        # take it's children and add them to the start
        # of the queue
        queue = deque(self.graph.successors(path))
        while queue:
            path = queue.pop()
            children = self.graph.successors(path)
            queue.extendleft(children)

            path = self._deroot_path(path)
            yield path

    def bfs(self, path=None):
        if path:
            self._validate_path(path)
        path = self._root_path(path)

        # pop the next node in the queue
        # take it's children and add them to the end
        # of the queue
        queue = deque(self.graph.successors(path))
        while queue:
            path = queue.pop()
            children = self.graph.successors(path)
            queue.extend(children)

            path = self._deroot_path(path)
            yield path
