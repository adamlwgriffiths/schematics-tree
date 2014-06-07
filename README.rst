===============
Schematics-Tree
===============

Provides real-time inspection of classes using Schematic's Model and Type classes.

A central registry is provided which stores Models in a Tree using user provided paths.
This registry can then be explored and manipulated in real-time.

A Flask application is included to allow viewing an application's data over HTTP.


Design
======

The registry is a tree structure built on top of a networkx graph.

The registry stores models using weak pointers, so you don't need to worry about memory
management. Currently, the tree is only cleaned up when you remove a model.


Properties are represented with a Property class. This redirects requests for its
'value' property to the model's value.

New property wrappers can be specified by adding to the 'Registry.properties' dictionary.
This is a dictionary of 'type class : property class' pairs.
If the matching type is not found in the dictionary, the default 'Property' type is used.


Examples
========


Register models and run web server
----------------------------------

::

    from __future__ import absolute_import, print_function, division, unicode_literals

    from schematics.types import StringType
    from schematics.models import Model

    class Person(Model):
        first_name = StringType(required=True)
        last_name = StringType(required=True)


    from schematics_tree.model import TreeModel
    from schematics_tree.registry import Registry, initialise, shutdown, registry
    from schematics_tree.tree import TreeGraph
    from schematics_tree.flask import create

    initialise()

    adam = Person({'first_name':'Adam','last_name':'Griffiths'})
    registry().add_model('/people/adam', adam)
    # adam and monty are friends
    registry().add_model('/people/monty/friends/adam', adam)

    monty = Person({'first_name':'Monty','last_name':'Python'})
    registry().add_model('/people/monty', monty)
    registry().add_model('/people/adam/friends/monty', monty)

    joey = Person({'first_name':'Joey','last_name':'JoeJoeJoe'})
    registry().add_model('/people/joey', joey)
    # joey and adam are friends
    registry().add_model('/people/adam/friends/joey', joey)

    app = create()
    app.run(debug=True, use_debugger=True, use_reloader=True, host='0.0.0.0')

    shutdown()


Adding / Removing Models
------------------------

The registry is accessible via the registry() function.
Each model resides at a unique path within the tree.

::

    >>> registry().add_model('/people/adam', adam)


TreeModel extends Schematics Model class and receives a path value.
It registers itself with the tree during construction.

::

    class Person(TreeModel):
        first_name = StringType(required=True)
        last_name = StringType(required=True)

    >>> adam = Person('/people/adam', {'first_name':'Adam','last_name':'Griffiths'})
    >>> registry().values('/people/adam')
    {'first_name': 'Adam', 'last_name': 'Griffiths'}


A path can only contain a single model, attempting to add more will result in a
ValueError exception being thrown.

::

    >>> registry().add_model('/people/adam', adam)
    >>> registry().add_model('/people/adam', monty)
    ValueError: Path already has a model


When you remove a model, any redundant paths are trimmed from the tree.

::

    >>> registry().node('/people/adam', values=True)
    {'first_name': 'Adam', 'last_name': 'Griffiths'}
    # this node has sub nodes, the model and its values will be removed
    # but the node will remain and still be accessible
    >>> registry().remove_model('/people/adam')
    >>> registry().node('/people/adam')
    {}


::

    >>> registry().node('/people/joey', values=True)
    {'first_name': 'Joey', 'last_name': 'JoeJoeJoe'}
    # this node has no children and will be removed.
    # further access will result in an error
    >>> registry().remove_model('/people/joey')
    >>> registry().node('/people/joey')
    KeyError: u'root/people/joey'


Adding new type handlers
------------------------

You can add types to the Registry.properties dictionary to handle
values not trivially supported.

::

    from schematics_tree import Registry, Property, TreeModel
    from schematics.types.base import BaseType

    class MyType(BaseType):
        '''custom schematics type
        '''
        # implementation of schematics type goes here
        pass

    class MyModel(TreeModel):
        ''' model using custom schematics type
        '''
        value = MyType()

    class MyProperty(Property):
        '''property that handles getting and setting values for custom type
        '''
        @property
        def value(self):
            model = self.model()
            if model:
                data = model._data[self.field]
                # do something with the data
                return data
            return None

        @value.setter
        def value(self, value):
            model = self.model()
            if model:
                # do something with the value
                model._data[self.field] = value

    # register the property handler
    Registry.properties[MyType] = MyProperty


Exploring
---------

'nodes' method returns a list of full keys for all nodes.

::

    >>> registry().nodes()
    [u'/people', u'/people/monty/friends/adam', u'/people/adam/friends/monty', u'/people/adam/friends/joey', u'/people/joey', u'/people/monty/friends', u'/people/adam/friends', u'/people/adam', u'/people/monty']


'children' returns a list of full keys for the children of the specified node.
If no node is specified, the root is assumed.

::

    >>> registry().children()
    [u'/people']
    >>> registry().children('/people')
    [u'/people/adam', u'/people/joey', u'/people/monty']


'parent' returns the full key for the parent of the specified node.
If the specified node is a top level node, None is returned.

::

    >>> registry().parent('/people/adam')
    /people
    >>> registry().parent('/people')
    None


'tree' returns a dict-of-dicts representation of the tree's paths (without values) from
the specified node.
If no node is specified, the root is assumed.

::

    >>> registry().tree()
    {u'people': {u'adam': {u'friends': {u'monty': {}, u'joey': {}}}, u'monty': {u'friends': {u'adam': {}}}, u'joey': {}}}
    >>> registry().tree('/people')
    {u'adam': {u'friends': {u'monty': {}, u'joey': {}}}, u'monty': {u'friends': {u'adam': {}}}, u'joey': {}}


Getting and Setting Values
--------------------------

The node() method returns a dictionary of the properties at the specified path.

::

    >>> registry().node('/people/adam')
    {'first_name': <schematics_tree.registry.Property object at 0x1033c2ad0>, 'last_name': <schematics_tree.registry.Property object at 0x1033c2b10>}


To make the properties human readable, set 'values=True'.

::

    >>> registry().node('/people/adam', values=True)
    {'first_name': 'Adam', 'last_name': 'Griffiths'}


The 'value' property of the Property object supports assignment.

::

    >>> registry().node('/people/adam')
    {'first_name': <schematics_tree.registry.Property object at 0x1033c2ad0>, 'last_name': <schematics_tree.registry.Property object at 0x1033c2b10>}
    >>> registry().node('/people/adam')['first_name'].value
    'Adam'
    >>> registry().node('/people/adam')['first_name'].value = 'Not Adam'
    >>> registry().node('/people/adam')['first_name'].value
    'Not Adam'


Adding, deleting or modifying contents the contents of the returned dictionary
will not be reflected in the tree or by the models.

Use the 'value' property of the Property object as mentioned above to make changes.


::

    >>> registry().node('/people/adam', values=True)
    {'first_name': 'Adam', 'last_name': 'Griffiths'}
    >>> registry().node('/people/adam', values=True)['first_name'] = 'Not Adam'
    >>> registry().node('/people/adam', values=True)
    {'first_name': 'Adam', 'last_name': 'Griffiths'}


::

    >>> registry().node('/people/adam', values=True)
    {'first_name': 'Adam', 'last_name': 'Griffiths'}
    >>> del registry().node('/people/adam', values=True)['first_name']
    >>> registry().node('/people/adam', values=True)
    {'first_name': 'Adam', 'last_name': 'Griffiths'}



Changing the separator character
--------------------------------

The default separator character is '/'. This can be changed before the registry is created.

::

    from schematics_tree import Registry
    Registry.separator = '.'


Flask end points
================

Schematics-tree provides an optional flask application that allows for the viewing
and modification of model values over HTTP.

There is currently no authentication / security mechanism, so avoid using this
for internet-connected systems.


Create a default application
----------------------------

If you're not using flask in your application, this function will create a flask
application and set it up for you.

The web page will be accessible at 'http://localhost:8080/'

::

    from schematics_tree.flask import create
    app = create()
    app.run(debug=True, use_debugger=True, use_reloader=True, host='0.0.0.0')



If you already have a flask application, you can add the schematics-tree views to
it using the 'register_blueprints' function.

The web page will be accessible at 'http://<host:port>/<url_prefix>/'

::

    from flask import Flask
    from schematics_tree.flask import register_blueprints

    app = Flask(__name__)
    # url_prefix is None
    # provide a url_prefix to avoid clashing with your application
    def register_blueprints(app, url_prefix='/path/goes/here'):


/keys/<path>
-----

Provides a list of keys, in full key format, from the specified starting path.

All keys are returned when you don't specify a parent.

http://.../keys::

    ["/people", "/people/monty/friends/adam", "/people/adam/friends/monty", "/people/adam/friends/joey", "/people/joey", "/people/monty/friends", "/people/adam/friends", "/people/adam", "/people/monty"]


Only children are returned when you request a specified path.

http://.../keys/people::

    ["/people/adam", "/people/joey", "/people/monty"]


/tree/<path>
------------

Provides a view of the tree, as a dictionary of dictionaries, from the specified starting path.

http://.../tree::

    {"people": {"adam": {"friends": {"monty": {}, "joey": {}}}, "monty": {"friends": {"adam": {}}}, "joey": {}}}


http://...tree/people/adam::

    {"friends": {"monty": {}, "joey": {}}}


/nodes/<path>
-------------

Provide the values of a specified path.

http://.../nodes/people/adam::

    {"first_name": "Adam", "last_name": "Griffiths"}


Dependencies
============
* schematics
* networkx
* flask (optional)


TODO
====

* Add setup.py
* Add tests
* Test and support more schematics types (string, int, float, url, numpy, etc)
* Provide an AJAX powered web page which provides exploration, and the viewing and setting of values.
* Prune the tree more often than just in remove_model.
* Provide a security / login decorator for the flask views
