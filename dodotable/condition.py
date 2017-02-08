# -*- coding: utf-8 -*-
""":mod:`dodotable.condition` --- Hello filter!
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""
import six
from sqlalchemy.sql.expression import asc, desc, or_

from .exc import BadChoice
from .schema import Queryable, Renderable, Schema
from .util import camel_to_underscore, _get_data


class _Filter(Schema):
    """Base class for filter results of table."""

    pass


class SelectFilter(_Filter, Renderable):
    """여러 옵션중 하나를 선택하는 필터를 만듭니다.

    :param cls:
    :param attribute_name:
    :param choices:
    :param request_args:
    :type request_args: :class:`werkzeug.datastructures.MultiDict`
    :param default:

    """

    def __init__(self, cls, attribute_name, choices, request_args,
                 default=None):
        self.cls = cls
        self.attribute = getattr(cls, attribute_name)
        self.attribute_name = attribute_name
        self.request_args = request_args
        self.choices = [{'name': 'all', 'description': u'모두'}] + choices
        self.default = default

    def __query__(self):
        arg_name = 'select.{}'.format(self.attribute_name)
        s = self.request_args.get(arg_name, self.default)
        choices = [c['name'] for c in self.choices]
        if not s:
            q = self.attribute.in_(choices)
        elif s not in choices:
            raise BadChoice(description='Invalid choices for `{}`: {}'.format(
                arg_name,
                s
            ))
        elif s == 'all':
            q = None
        else:
            q = self.attribute == s
        return q

    def __html__(self):
        return self.render('select_filter.html', filter=self)


def create_search_name(name):
    """HTML form의 name을 생성합니다.

    :param cls:
    :return:

    """
    return {'word': 'search_{}.word'.format(name),
            'type': 'search_{}.type'.format(name)}


class Ilike(Queryable):
    """SQL ILIKE 연산을 담당하는 필터

    :class:`~Column` 에 포함 가능한 필터로, 단어를 받아서 그 단어에 대한 조건을
    생성합니다.

    .. code-block:: python

       >>> print(Ilike(Music, 'name', request_args))
       lower(music.name) LIKE lower(:name_1)

    :param cls:
    :param attribute_name:
    :param request_args:

    """

    def __init__(self, cls, attribute_name, request_args):
        self.cls = cls
        self.attribute = getattr(cls, attribute_name)
        self.attribute_name = attribute_name
        self.request_args = request_args

    def __query__(self):
        name = create_search_name(camel_to_underscore(self.cls.__name__))
        type_ = self.request_args.get(name['type'])
        word = self.request_args.get(name['word'])
        q = None
        if type_ == self.attribute_name:
            q = self.attribute.ilike(u'%{word}%'.format(word=word))
        return q


class IlikeAlias(Ilike):
    """sqlalchemy alias 를 위한 ilike 필터.

    :param identifier:
    :param alias_attr:
    :param request_args:
    :type request_args: :class:`werkzeug.datastructures.MultiDict`

    """

    def __init__(self, identifier, alias_attr, request_args):
        self.identifier = identifier
        self.alias_attr = alias_attr
        self.request_args = request_args

    def __query__(self):
        name = create_search_name(self.identifier)
        word = self.request_args.get(name['word'])
        type = self.request_args.get(name['type'])
        q = None
        if word and type == self.alias_attr.name:
            q = self.alias_attr.ilike(u'%{word}%'.format(word=word))
        return q


class IlikeSet(_Filter, Queryable, Renderable):
    """모든 ILIKE 관련 연산을 묶습니다.

    :class:`~Table` 에 포함 가능한 필터로, 해당 테이블에 있는 ILIKE 조건을 묶어서
    OR 연산으로 묶습니다.

    .. code-block:: python

       >>> table = Table(AdminRole, columns=[...])
       >>> table.add_filter(IlikeSet(table, request_args))
       >>> print(table.query)
       SELECT ...
       FROM admin_role AS admin_role_1
       ...
       WHERE lower(name) LIKE lower(:name_1)
         OR lower(authority) LIKE lower(:authority_1)
       ...

    :param table:
    :type table: :class:`dodotable.Table`
    :param request_args:
    :type request_args: :class:`werkzeug.datastructures.MultiDict`
    :param identifier:

    """

    def __init__(self, table, request_args, identifier=None):
        self.table = table
        if not identifier:
            identifier = camel_to_underscore(table.cls.__name__)
        name = create_search_name(identifier)
        self.arg_name = name['word']
        self.arg_type_name = name['type']
        self.request_args = request_args

    def __query__(self):
        filter_ = []
        for column in self.table._columns:
            for f in column.filters:
                if isinstance(f, Ilike) and f.__query__() is not None:
                    filter_.append(f.__query__())

        return or_(*filter_) if filter_ else None

    def __html__(self):
        return self.render('ilike_set.html', filter=self)


class Order(Queryable):
    """정렬 조건을 내보냅니다.

    :param cls:
    :param attribute_name:
    :param order:
    """

    #: 내림차순
    DESCENDANT = 'desc'

    #: 오름차순
    ASCENDANT = 'asc'

    def __init__(self, cls, attribute_name, order=None):
        self.cls = cls
        self.order = order or self.DESCENDANT
        self.attribute = _get_data(cls, attribute_name, attribute_name)

    @classmethod
    def asc_order_name(cls, attr):
        return '{attr}.{order}'.format(attr=attr, order=cls.ASCENDANT)

    @classmethod
    def desc_order_name(cls, attr):
        return '{attr}.{order}'.format(attr=attr, order=cls.DESCENDANT)

    @classmethod
    def of_column(cls, attr, order_by):
        asc_order = cls.asc_order_name(attr)
        desc_order = cls.desc_order_name(attr)
        order = None
        if not order_by or not isinstance(order_by, six.string_types):
            return None
        for o in order_by.split(','):
            if o.strip() == asc_order:
                order = cls.ASCENDANT
            elif o.strip() == desc_order:
                order = cls.DESCENDANT
        return order

    def __query__(self):
        if self.order == self.DESCENDANT:
            query = desc(self.attribute)
        elif self.order == self.ASCENDANT:
            query = asc(self.attribute)
        return query
