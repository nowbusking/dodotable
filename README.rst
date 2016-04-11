dodotable
=========

HTML table representation for `SQLAlchemy`_ .

.. _SQLAlchemy: http://www.sqlalchemy.org/


SQLAlchemy to ``<table>``
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from dodotable.schema import Table

   table = Table(
       cls=Music,
       label='music table',
       columns=[
           Column(attr='id', label=u'id'),
           Column(attr='name', label=u'name'),
       ],
       sqlalchemy_session=session
   )
   print(table.select(offset=0, limit=10).__html__())
