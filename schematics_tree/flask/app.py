from __future__ import absolute_import, print_function, division, unicode_literals
from flask import Flask
from .view import blueprint
from .sockets import register_websockets

def create(*args, **kwargs):
    app = Flask(__name__, *args, **kwargs)
    register_blueprints(app)
    register_websockets(app)
    return app

def register_blueprints(app, url_prefix=None):
    app.register_blueprint(blueprint, url_prefix=url_prefix)
