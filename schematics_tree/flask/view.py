from __future__ import absolute_import, print_function, division#, unicode_literals
# can't import unicode literals or we break flask
import json
from flask import Blueprint, abort
from flask.views import MethodView
from networkx import NetworkXException
from ..registry import registry

blueprint = Blueprint('schematics_tree', __name__)

class KeysView(MethodView):
    def get(self, node=None, **kwargs):
        try:
            # no args = get all keys
            # args = get child keys
            if node:
                node = registry().separator + node
                response = registry().children(node)
            else:
                response = registry().nodes()
            return json.dumps(response)
        except NetworkXException as e:
            print(e)
            abort(404)

class TreeView(MethodView):
    def get(self, node=None, **kwargs):
        try:
            if node:
                node = registry().separator + node
            response = registry().tree(node)
            return json.dumps(response)
        except NetworkXException as e:
            print(e)
            abort(404)

class ValuesView(MethodView):
    def get(self, node, **kwargs):
        try:
            # add the separator prefix
            node = registry().separator + node
            # get the values for the specified node
            response = registry().node(node, values=True)
            return json.dumps(response)
        except NetworkXException as e:
            abort(404)

    def put(self, node, **kwargs):
        # set the values for the specified node
        try:
            node = registry().node(node)
            for k,v in kwargs.items():
                node[k].value = v
        except NetworkXException as e:
            print(e)
            abort(404)
        else:
            for k,v in kwargs.items():
                node[k] = v

            return self.get(node)


blueprint.add_url_rule('/keys', strict_slashes=False, view_func=KeysView.as_view('all_keys'))
blueprint.add_url_rule('/keys/<path:node>', strict_slashes=False, view_func=KeysView.as_view('child_keys'))
blueprint.add_url_rule('/tree', strict_slashes=False, view_func=TreeView.as_view('full_tree'))
blueprint.add_url_rule('/tree/<path:node>', strict_slashes=False, view_func=TreeView.as_view('sub_tree'))
blueprint.add_url_rule('/values/<path:node>', strict_slashes=False, view_func=ValuesView.as_view('values'))
