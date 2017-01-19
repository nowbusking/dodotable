dodotable
=========

.. image:: https://badge.fury.io/py/dodotable.svg?
   :target: https://pypi.python.org/pypi/dodotable
   :alt: Latest PyPI version

.. image:: https://readthedocs.org/projects/dodotable/badge/
   :target: https://dodotable.readthedocs.org/
   :alt: Documentation Status

.. image:: https://travis-ci.org/spoqa/dodotable.svg?branch=master
   :target: https://travis-ci.org/spoqa/dodotable

HTML table representation for `SQLAlchemy`_ .

.. _SQLAlchemy: http://www.sqlalchemy.org/


SQLAlchemy to ``<table>``
~~~~~~~~~~~~~~~~~~~~~~~~~

Assume you have an entity called `Music`. It looks like the below.

.. code-block:: python

   class Music(Base):

       id = Column(Integer, primary_key=True)

       name = Column(Unicode, nullable=False)


The following code renders a sortable <table> consisting of a list of music.

.. code-block:: python

   from dodotable.schema import Table, Column

   table = Table(
       cls=Music,
       label='music table',
       columns=[
           Column(attr='id', label=u'id', order_by='id.desc'),
           Column(attr='name', label=u'name'),
       ],
       sqlalchemy_session=session
   )
   print(table.select(offset=0, limit=10).__html__())


Using with Flask_
~~~~~~~~~~~~~~~~~

Flask_ uses Jinja2_ as the template engine. As they mentioned on
document[1]_, it is one of strategy that implement ``__html__`` on every class
inherit ``dodotable.schema.Renderable`` to convert a instance into HTML
directly in Jinja2_. Re-write the example written before with Flask_.


.. code-block:: python

   from dodotable.schema import Table, Column
   from flask import Flask, render_template, request

   app = Flask(__name__)


   @app.route('/musics/', methods=['GET'])
   def list_musics():
       table = Table(
           cls=Music,
           label='music table',
           columns=[
               Column(attr='id', label=u'id',
                      order_by=request.args.get('order_by')),
               Column(attr='name', label=u'name'),
           ],
           sqlalchemy_session=session
       )
       return render_template(
           'list_musics.html',
           table=table.select(limit=request.args.get('limit'),
                              offset=request.args.get('offset'))
       )

And ``list_musics.html`` which is jinja2 template is look like below.

.. code-block::

   <html>
     <body>
       {{ table }}
     </body>
   </html>


.. _Flask: http://flask.pocoo.org
.. _Jinja2: http://jinja.pocoo.org

.. [1] http://jinja.pocoo.org/docs/dev/api/#jinja2.Markup
