# -*- coding: utf-8 -*-
""":mod:`dodotable.schema` --- table schema
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""
from __future__ import absolute_import

import collections
try:
    from collections.abc import MutableSequence
except ImportError:
    from collections import MutableSequence
import math

from sqlalchemy.orm import Query

from .environment.flask import FlaskEnvironment
from .util import render, string_literal, _get_data


__all__ = (
    'Cell', 'Column', 'ENVIRONMENT', 'Queryable', 'Renderable',
    'Row', 'Table', 'Pager', 'Schema',
)


ENVIRONMENT = FlaskEnvironment()


class Schema(object):
    """

    :param environment:
    :type environment: :class:`~.environment.Environment`

    """

    environment = ENVIRONMENT

    def render(self, template_name, **kwargs):
        return render(template_name,
                      extra_environments=self.environment.__dict__(),
                      **kwargs)


class Renderable(object):
    """jinja에서 바로 렌더링되는 클래스의 상위 클래스

    jinja에서는 ``__html__`` 를 호출하여 렌더링을 하므로
    :class:`~Renderable` 을 상속받아 :meth:`~Renderable.__html__` 을
    구현하는 경우 바로 렌더링 할 수 있습니다.

    .. code-block:: python

       class SomeElem(Renderable):

           def __html__(self):
                return "<h1>Hello World</h1>"

    .. code-block:: jinja

       {{ SomeElem() }} <!-- == <h1>Hello World</h1> -->

    """

    def __html__(self):
        """:mod:`jinja` 내부 호출용 함수

        .. note::

           요즘은 :func:`__html__` 을 구현하는게 HTML 뱉는 객체의 de facto 라고하더군요.

        """
        raise NotImplementedError('__html__ not implemented yet.')


class Queryable(object):
    """:class:`~sqlalchemy.orm.query.Query` 로 변환 가능한 객체

    쿼리를 내뱉는 모든 필더들은 :class:`~Queryable` 을 상속받고
    :meth:`~Queryable.__query__` 를 구현하여 sqlalchemy 쿼리로 사용할 수 있도록
    변환해야합니다.

    """

    def __query__(self):
        """모든 :class:`~dodotable.Queryable` 객체가 구현해야하는 메소드."""
        raise NotImplementedError('__query__ not implemented yet.')


class Cell(Schema, Renderable):
    """테이블의 셀을 나타내는 클래스

    :param int col: column 위치
    :param int row: row 위치
    :param data: 셀에 채워질 데이터
    """

    def __init__(self, col, row, data, _repr=string_literal, classes=()):
        self.col = col
        self.row = row
        self.data = data
        self.repr = _repr
        self.classes = classes

    def __html__(self):
        return self.render('cell.html', cell=self)


class LinkedCell(Cell):
    """컨텐츠에 링크가 걸린 Cell

    :param int col: column 위치
    :param int row: row 위치
    :param data: 셀에 채워질 데이터
    :param endpoint: 데이터를 누르면 이동할 url

    """

    def __init__(self, col, row, data, endpoint):
        self.col = col
        self.row = row
        self.data = data
        self.url = endpoint

    def __html__(self):
        return self.render('linkedcell.html', cell=self)


class Column(Schema, Renderable):
    """테이블의 열을 나타내는 클래스

    :param str label: 컬럼 레이블
    :param str attr: 가져올 attribute 이름
    :param list order_by: 정렬 기준
    :param list filters: 정렬 기준
    :param function _repr: 보여질 형식
    :param bool sortable: 정렬 가능 여부
    :param bool visible: 테이블에 해당 칼럼이 보일지 말지의 여부.
                         해당 값이 False여도
                         :class:`~dodotable.condition.IlikeSet`의 필터에는
                         보이므로 검색에는 사용할 수 있습니다.

    """

    def __init__(self, label, attr, order_by=(), filters=[],
                 _repr=string_literal, sortable=True, visible=True,
                 classes=()):
        from .condition import Order
        self.label = label
        self.attr = attr
        self.filters = filters
        self.order_by = Order.of_column(attr, order_by)
        self._repr = _repr
        self.sortable = sortable
        self.visible = visible
        self.classes = classes

    def add_filter(self, filter):
        self.filters.append(filter)

    def __cell__(self, col, row, data, attribute_name, default=None):
        """해당 열의 데이터를 :class:`~dodotable.Cell`로 변환합니다.

        :param col:
        :param row:
        :param data:
        :param attribute_name:
        :param default:
        :return:
        """
        return Cell(col=col, row=row,
                    data=_get_data(data, attribute_name, default),
                    _repr=self._repr,
                    classes=self.classes)

    def __html__(self):
        return self.render('column.html', column=self)


class LinkedColumn(Column):
    """링크가 걸려야 하는 열 나타내는 클래스

    :param str label: 컬럼 레이블
    :param str attr: 가져올 attribute 이름
    :param str or function endpoint: 걸릴 링크 형식
    :param list order_by: 정렬 기준

    """

    def __init__(self, *args, **kwargs):
        self.endpoint = kwargs.pop('endpoint')
        super(LinkedColumn, self).__init__(*args, **kwargs)

    def __cell__(self, col, row, data, attribute_name, default=None):
        endpoint = self.endpoint(data) if callable(
            self.endpoint) else self.endpoint
        return LinkedCell(col=col, row=row,
                          data=_get_data(data, attribute_name, default),
                          endpoint=endpoint)


class Row(Schema, MutableSequence, Renderable):
    """테이블에 행을 나타내는 클래스 """

    def __init__(self):
        self._row = []

    def __delitem__(self, key):
        del self._row[key]

    def __getitem__(self, item):
        return self._row[item]

    def __setitem__(self, key, value):
        self._row[key] = value

    def __len__(self):
        return len(self._row)

    def insert(self, index, object_):
        self._row.insert(index, object_)

    def append(self, cell):
        """행에 cell을 붙입니다. """
        assert isinstance(cell, Cell)
        super(Row, self).append(cell)

    def __html__(self):
        return self.render('row.html', row=self)


class Pager(Schema, Renderable):

    DEFAULT_LIMIT = 10

    DEFAULT_OFFSET = 0

    Page = collections.namedtuple('Page',
                                  ['selected', 'number', 'limit', 'offset'])

    def __init__(self, limit, offset, count, padding=10):
        try:
            self.limit = int(limit)
            self.offset = int(offset)
            self.count = int(count)
            self.padding = int(padding)
        except ValueError:
            self.limit = 10
            self.offset = 0
            self.count = 0
            self.padding = 10

    def from_page_number(self, number):
        return self.Page(limit=self.limit, offset=(number - 1) * self.limit,
                         selected=False, number=number)

    @property
    def pages(self):
        page_count = int(math.ceil(self.count / float(self.limit)))
        current_page_count = (self.offset // self.limit) + 1
        pages = []
        s = (current_page_count - 1) // self.padding
        start = s * 10 + 1
        for page in self.range(start,
                               start + self.padding - 1,
                               max_=page_count):
            selected = False
            if page == current_page_count:
                selected = True
            p = self.Page(selected=selected, number=page, limit=self.limit,
                          offset=self.limit * (page - 1))
            pages.append(p)
        return pages

    def range(self, start, end, max_, min_=1):
        i = start
        yield min_
        while i <= end and i <= max_:
            if i > min_:
                yield i
            i += 1
        if i < max_:
            yield max_

    def __html__(self):
        return self.render('pager.html', pager=self)


class Table(Schema, Queryable, Renderable):
    """데이터를 나타내는 테이블의 틀

    :param cls:
    :param label:
    :param columns:
    :param sqlalchemy_session:

    """

    def __init__(self, cls, label, unit_label="row",
                 columns=[],
                 sqlalchemy_session=None):
        self.cls = cls
        self.label = label
        self.unit_label = unit_label
        self._filters = []
        self.rows = []
        self._columns = columns
        self._count = None
        self.session = sqlalchemy_session
        try:
            if sqlalchemy_session is None:
                self.session = self.environment.get_session()
        finally:
            if not self.session:
                raise ValueError("{0.__class__.__name__}.session "
                                 "can't be None".format(self))
        self.pager = Pager(limit=1, offset=0, count=0)
        self.pager.environment = self.environment

    def select(self, offset, limit):
        self.rows = []
        q = self.query.offset(offset).limit(limit)
        for i, row in enumerate(q):
            _row = Row()
            for j, col in enumerate(self.columns):
                _row.append(
                    col.__cell__(col=j, row=i, data=row,
                                 attribute_name=col.attr)
                )
            self.rows.append(_row)
        self.pager = Pager(limit=limit, offset=offset,
                           count=self.count)
        self.pager.environment = self.environment
        return self

    def add_filter(self, filter):
        self._filters.append(filter)

    @property
    def _order_queries(self):
        """쿼리의 정렬 조건을 가져옵니다."""
        from .condition import Order
        order = []
        for column in self.columns:
            if column.order_by:
                o = Order(self.cls, column.attr, column.order_by)
                order.append(o.__query__())
        if not order:
            k = self.columns[0].attr
            o = Order(self.cls, k)
            self.columns[0].order_by = o.order
            order.append(o.__query__())
        return order

    @property
    def _filter_queries(self):
        for filter in self._filters:
            if filter:
                yield filter.__query__()

    @property
    def count(self):
        return self.build_base_query().count()

    def build_base_query(self):
        if isinstance(self.cls, Query):
            query = self.cls
        else:
            query = self.session.query(self.cls)
        for filter in self._filter_queries:
            if filter is not None:
                query = query.filter(filter)
        return query

    @property
    def query(self):
        """쿼리를 만듭니다.

        :return:
        """
        query = self.build_base_query().order_by(*self._order_queries)
        return query

    @property
    def columns(self):
        return [column for column in self._columns if column.visible]

    def __html__(self):
        return self.render('table.html', table=self)

    def __query__(self):
        return self.query
