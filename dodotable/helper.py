""":mod:`dodotable.helper` --- helper
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""
from .schema import Renderable, Queryable


__all__ = 'Limit',


class Limit(Renderable, Queryable):
    """querystring 중에 ``limit``\ 를 조작해서 100개보기 같은 기능을 제공합니다."""

    def __init__(self, table, request_args, identifier=None):
        self.table = table
        self.request_args = request_args
        if not identifier:
            identifier = camel_to_underscore(table.cls.__name__)
        self.arg_type_name = 'limit_{}'.format(identifier)

    def __query__(self):
        pass

    def __html__(self):
        return render('limit.html', filter=self)

