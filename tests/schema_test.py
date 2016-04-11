# -*- coding: utf-8 -*-
from dodotable.schema import Cell, Column, Row, Table, Pager
from mock import patch, PropertyMock

from .entities import Music
from .helper import (compare_html, DodotableTestEnvironment, pager_html,
                     table_html)


def test_cell():
    s = 'hello world'
    c = Cell(0, 0, s)
    expected = '<td>{data}</td>'.format(data=s)
    assert compare_html(c.__html__(), expected)


@patch('dodotable.schema.Schema.environment', new_callable=PropertyMock,
       return_value=DodotableTestEnvironment())
def test_row(environ):
    expected = '<tr>'
    row = Row()
    for n in range(0, 10):
        cell = Cell(0, n, n)
        row.append(cell)
        expected += '<td>{}</td>'.format(cell.data)
    expected += '</tr>'
    assert compare_html(row.__html__(), expected)


@patch('dodotable.schema.Schema.environment', new_callable=PropertyMock,
       return_value=DodotableTestEnvironment())
def test_column(environ):
    column_label = 'name'
    column_key = 'name'
    expected = '''
        <th class="order-none ">
            <a href="/?order_by={attr}.desc">{label}</a>
        </th>
    '''.format(attr=column_key, label=column_label)
    column = Column(attr=column_key, label=column_label)
    column.environment = DodotableTestEnvironment()
    assert compare_html(column.__html__(), expected)


@patch('dodotable.schema.Schema.environment', new_callable=PropertyMock,
       return_value=DodotableTestEnvironment())
def test_table(environ, fx_session, fx_music):
    q = fx_session.query(Music) \
        .order_by(Music.id.desc())
    expected_rows = ''
    for music in q:
        expected_rows += u'''
        <tr>
            <td>{id}</td>
            <td>{name}</td>
        </tr>
        '''.format(id=music.id, name=music.name)
    table_label = u'테스트'
    table = Table(
        cls=Music,
        label=table_label,
        columns=[
            Column(attr='id', label=u'id', order_by='id.desc'),
            Column(attr='name', label=u'이름'),
        ],
        sqlalchemy_session=fx_session
    )
    column_html = u'''<tr><th class="order-desc ">
      <a href="/?order_by=id.asc">id</a>
    </th>
    <th class="order-none ">
      <a href="/?order_by=name.desc">이름</a>
    </th>
    </tr>
    '''
    expected = table_html(count=q.count(), rows=expected_rows,
                          filters='', columns=column_html,
                          title=table_label, pager=pager_html,
                          unit_label=u'row')
    html = table.select(offset=0, limit=10).__html__()
    assert compare_html(html, expected)


class TestCell(Cell):

    def __html__(self):
        return '<td><button>{}</button></td>'.format(self.data)


class TestColumn(Column):

    def __cell__(self, col, row, data, attribute_name, default=None):
        return TestCell(col=col, row=row,
                        data=getattr(data, attribute_name, default))


def test_custom_cell(fx_session, fx_music):
    fx_session.commit()
    table = Table(cls=Music, label='hello', columns=[
        TestColumn(label=u'hello', attr='id', order_by='id.desc')
    ], sqlalchemy_session=fx_session)
    table.select(offset=0, limit=10)
    row = table.rows[0]
    music = fx_session.query(Music).order_by(Music.id.desc()).first()
    expected = '<tr><td><button>{}</button></td></tr>'.format(music.id)
    actual = row.__html__()
    assert compare_html(actual=actual, expected=expected)


def to_page(l, current):
    for n in l:
        yield Pager.Page(number=n, selected=(n == current),
                         limit=10, offset=((n - 1) * 10))


def test_pager():
    pager = Pager(count=1000, limit=10, offset=0)
    p = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 100]
    assert pager.pages == list(to_page(p, 1))
    pager = Pager(count=1000, limit=10, offset=40)
    p = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 100]
    assert pager.pages == list(to_page(p, 5))
    pager = Pager(count=1000, limit=10, offset=100)
    p = [1, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 100]
    assert pager.pages == list(to_page(p, 11))
    pager = Pager(count=1000, limit=10, offset=940)
    p = [1, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100]
    assert pager.pages == list(to_page(p, 95))
    pager = Pager(count=1000, limit=10, offset=90)
    p = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 100]
    assert pager.pages == list(to_page(p, 10))
