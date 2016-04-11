# -*- coding: utf-8 -*-
""":mod:`dodotable.helper` --- helper
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""
from .schema import Queryable, Renderable, Schema
from .util import camel_to_underscore


__all__ = 'Limit',


class _Helper(Schema):
    pass


class Limit(_Helper, Renderable, Queryable):
    """querystring 중에 ``limit``\ 를 조작해서 100개보기 같은 기능을
    제공합니다.

    """

    def __init__(self, table, request_args, identifier=None):
        self.table = table
        self.request_args = request_args
        if not identifier:
            identifier = camel_to_underscore(table.cls.__name__)
        self.arg_type_name = 'limit_{}'.format(identifier)

    def __query__(self):
        pass

    def __html__(self):
        return self.render('limit.html', filter=self)


def monkey_patch_environment(environ):
    modules = 'dodotable.schema', 'dodotable.condition', 'dodotable.helper'
    e = environ()
    for module_name in modules:
        module = __import__(module_name, globals(), locals(), ['*'], -1)
        for attr in dir(module):
            try:
                getattr(module, attr).environment = e
            except AttributeError:
                continue
