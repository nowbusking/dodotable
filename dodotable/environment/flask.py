# -*- coding: utf-8 -*-
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


__all__ = 'FlaskEnvironment', 'default_locale_selector'


class FlaskEnvironment(Environment):
    """Build table with :mod:`flask`"""

    def __init__(self, locale_selector=None, *args, **kwargs):
        if locale_selector is None:
            locale_selector = default_locale_selector
        super(FlaskEnvironment, self).__init__(
            *args,
            locale_selector=locale_selector,
            **kwargs
        )

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


def default_locale_selector():
    # FIXME
    # 현재 도도테이블을 사용하는 모든 Flask 서비스에서 공통적으로 정의되는
    # 로케일 판별 수단이 뭐가 있을지 모르겠어서 일단 임시로 리퀘스트의
    # accept_language를 사용합니다.
    try:
        return request.accept_languages.best_match(['ko', 'jp', 'en'])
    except:
        return 'ko'
