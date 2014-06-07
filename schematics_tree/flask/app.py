from __future__ import absolute_import, print_function, division, unicode_literals
from flask import Flask
from .view import blueprint

def create():
    app = Flask(__name__)
    register_blueprints(app)
    return app

def register_blueprints(app, url_prefix=None):
    app.register_blueprint(blueprint, url_prefix=url_prefix)
