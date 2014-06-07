from __future__ import absolute_import, print_function, division, unicode_literals
import networkx as nx
from weakref import ref
from collections import defaultdict
from .tree import TreeGraph


class Property(object):
    def __init__(self, model, field):
        self.model = ref(model)
        self.field = field

    @property
    def value(self):
        model = self.model()
        if model:
            return model._data[self.field]
        return None

    @value.setter
    def value(self, value):
        model = self.model()
        if model:
            model._data[self.field] = value

    def serialise(self):
        return self.value


class Registry(object):
    properties = {}

    def __init__(self, separator='/'):
        self.graph = TreeGraph(separator)

    @property
    def separator(self):
        return self.graph.separator

    def add_model(self, path, model):
        edge, node = self.graph.add(path)
        if 'model' in edge:
            raise ValueError('Path already has a model')
        edge['model'] = ref(model)
        for k,v in model._data.items():
            field = model._fields[k]
            prop = self.properties.get(field, Property)
            node[k] = prop(model, k)

    def remove_model(self, path):
        edge, node = self.graph.parent_edge(path), self.graph.node(path)
        # remove the model from the edge
        # clear the model properties from the node
        edge.clear()
        node.clear()
        # prune this branch
        self._prune(path)

    def _prune(self, path):
        # check down the tree for any other models
        # we don't want to delete nodes with child models
        for node in self.graph.dfs(path):
            parent_edge = self.graph.parent_edge(node)
            if 'model' in parent_edge:
                return

        # remove all children
        for node in self.graph.dfs(path):
            self.graph.remove(node)

        # remove parents until we hit a model
        current = path
        while current:
            # get the current node's parent edge
            edge = self.graph.parent_edge(current)
            # stop once we hit a node with a model in it
            if 'model' in edge:
                break
            # remove and get the parent
            self.graph.remove(current)
            current = self.graph.parent(current)

    def node(self, path, values=False):
        node = self.graph.node(path)
        if values:
            node = {
                k: v.value
                for k,v in node.items()
            }
        return node

    def parent(self, path):
        return self.graph.parent(path)

    def children(self, path=None):
        path = self.graph._root_path(path)
        children = self.graph.graph.successors(path)
        children = map(self.graph._deroot_path, children)
        return children

    def nodes(self, data=False):
        return self.graph.nodes(data)

    def tree(self, path=None):
        # construct a hierarchy of keys starting at the
        # specified path
        tree = {}
        for node in self.graph.dfs(path):
            # make local to the path
            node = node[len(path or ''):]
            # ignore the first separator
            nodes = node.split(self.graph.separator)[1:]
            t = tree
            for key in nodes:
                if key not in t:
                    t[key] = {}
                t = t[key]
        return tree


_registry = None
def registry():
    return _registry

def initialise(registry=None):
    global _registry
    _registry = registry or Registry()

def shutdown():
    global _registry
    _registry = None

