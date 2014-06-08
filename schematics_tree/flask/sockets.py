from __future__ import absolute_import, print_function, division#, unicode_literals
# can't import unicode literals or we break flask
from flask_sockets import Sockets
from geventwebsocket import WebSocketError
import json
from ..registry import registry

def register_websockets(app, url_prefix=None):
    sockets = Sockets(app)

    @sockets.route((url_prefix or '') + '/ws')
    def websocket_endpoint(ws):
        # register our listeners
        def model_added(sender, path, **kwargs):
            message = {
                'event':    'model_added',
                'path':     path,
            }
            ws.send(json.dumps(message))
        def model_removed(sender, path, **kwargs):
            message = {
                'event':    'model_removed',
                'path':     path,
            }
            ws.send(json.dumps(message))
        def path_added(sender, path, **kwargs):
            message = {
                'event':    'path_added',
                'path':     path,
            }
            ws.send(json.dumps(message))
        def path_removed(sender, path, **kwargs):
            message = {
                'event':    'path_removed',
                'path':     path,
            }
            ws.send(json.dumps(message))

        registry().model_added.connect(model_added)
        registry().model_removed.connect(model_removed)
        registry().path_added.connect(path_added)
        registry().path_removed.connect(path_removed)

        while True:
            try:
                message = ws.receive()

                # handle the message
                # TODO:

                response = {}
                ws.send(json.dumps(response))
            except WebSocketError as e:
                # websocket closed
                break
