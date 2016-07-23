""":mod:`dodotable.environment.flask` --- Flask environment
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Yet, dodotable only supports Jinja2_ for template, it can be possible to use
another template engine but if you have a mind to use Jinja2_,
maybe you have interest with Flask_ either.

Originally dodotable are intended to use with Flask_, so its environment class
is provided.


Customize HTML
==============

Maybe you wish to change a design of your table or add some help message,
give your class name on HTML elements. So all you have to do is inehrit
one of environment class, and use it in your table.

.. code-block:: python

   # yourapplication/dodotable.py
   from dodotable.schema import Column as SchemaColumn, Table as SchemaTable
   from dodotable.environment.flask import FlaskEnvironment
   from jinja2 import PackageLoader

   class CustomEnvironment(FlaskEnvironment):

       @property
       def template_loader(self):
           return PackageLoader('yourapplication', 'templates')


   class Column(SchemaColumn):

       environment = CustomEnvironment()


   class Table(SchemaTable):

       environment = CustomEnvironment()

.. code-block:: python

   #yourapplication/app.py
   from flask import Flask, render_template

   from .dodotable import Table, Column

   app = Flask(__name__)


   @app.route('/', methods=['GET'])
   def index():
       table = Table(columns=[
           Column(...)
       ], ...)
       return render_template('index.html', table=table.select(0, 10))


.. _Jinja2: http://jinja.pocoo.org/
.. _Flask: http://flask.pocoo.org/

"""
from __future__ import absolute_import
from flask import request

from . import Environment


__all__ = 'FlaskEnvironment',


class FlaskEnvironment(Environment):
    """Build table with :mod:`flask`"""

    def build_url(self, **kwargs):
        arg = request.args.copy()
        view_args = request.view_args
        arg.update(view_args)
        for attr in kwargs.keys():
            if attr in arg:
                arg.pop(attr)
        arg.update(kwargs.items())
        rule = request.url_rule
        result = rule.build(arg)
        return result[1]

    def get_session(self):
        ctx = request._get_current_object()
        try:
            session = ctx._current_session
        except AttributeError:
            return None
        else:
            return session
