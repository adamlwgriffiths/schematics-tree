from __future__ import absolute_import, print_function, division, unicode_literals
from schematics.models import Model
from .registry import registry

class TreeModel(Model):
    def __init__(self, path, *args, **kwargs):
        super(TreeModel, self).__init__(*args, **kwargs)
        self.path = path
        registry().add_model(path, self)
