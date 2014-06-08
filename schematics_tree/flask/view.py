from __future__ import absolute_import, print_function, division#, unicode_literals
# can't import unicode literals or we break flask
import json
from flask import Blueprint, abort, request
from flask.views import MethodView
from networkx import NetworkXException
from ..registry import registry

blueprint = Blueprint('schematics_tree', __name__)

class KeysView(MethodView):
    def get(self, path=None, **kwargs):
        try:
            # no args = get all keys
            # args = get child keys
            if path:
                path = registry().separator + path
                response = registry().children(path)
            else:
                response = registry().nodes()
            return json.dumps(response)
        except NetworkXException as e:
            abort(403)

class TreeView(MethodView):
    def get(self, path=None, **kwargs):
        try:
            if path:
                path = registry().separator + path
            response = registry().tree(path)
            return json.dumps(response)
        except NetworkXException as e:
            abort(403)

class ValuesView(MethodView):
    def get(self, path, **kwargs):
        try:
            # add the separator prefix
            path = registry().separator + path
            # get the values for the specified node
            response = registry().node(path, values=True)
            return json.dumps(response)
        except NetworkXException as e:
            abort(403)

    def put(self, path, **kwargs):
        original_path = path
        try:
            # add the separator prefix
            path = registry().separator + path
            node = registry().node(path)
            for k,v in kwargs.items():
                node[k].value = v
        except NetworkXException as e:
            abort(403)
        else:
            data = request.json
            if not data:
                abort(400)

            # set the values for the specified node
            for k,v in data.items():
                node[k].value = v

            # return the updated values
            return self.get(original_path)


blueprint.add_url_rule('/keys', strict_slashes=False, view_func=KeysView.as_view('all_keys'))
blueprint.add_url_rule('/keys/<path:path>', strict_slashes=False, view_func=KeysView.as_view('child_keys'))
blueprint.add_url_rule('/tree', strict_slashes=False, view_func=TreeView.as_view('full_tree'))
blueprint.add_url_rule('/tree/<path:path>', strict_slashes=False, view_func=TreeView.as_view('tree'))
blueprint.add_url_rule('/values/<path:path>', strict_slashes=False, view_func=ValuesView.as_view('values'))
