# -*- coding: utf-8 -*-
import re

from mock import PropertyMock, patch

from .entities import Music
from .helper import DodotableTestEnvironment, extract_soup
from dodotable.schema import Cell, Column, Row, Table, Pager


def test_cell():
    s = 'hello world'
    c = Cell(0, 0, s)
    cell_soup = extract_soup(c)
    assert cell_soup.find(
        'td',
        text=re.compile(re.escape(s)),
    )


@patch('dodotable.schema.Schema.environment', new_callable=PropertyMock,
       return_value=DodotableTestEnvironment())
def test_row(environ):
    row = Row()
    cell_length = 10
    for n in range(cell_length):
        cell = Cell(0, n, str(n))
        row.append(cell)
    row_soup = extract_soup(row)
    tr = row_soup.find('tr')
    assert len(tr.find_all('td')) == cell_length


@patch('dodotable.schema.Schema.environment', new_callable=PropertyMock,
       return_value=DodotableTestEnvironment())
def test_column(environ):
    column_label = 'Name'
    column_key = 'name'

    column = Column(attr=column_key, label=column_label)
    column.environment = DodotableTestEnvironment()
    column_soup = extract_soup(column)

    # Must provide link for sort by descending
    assert column_soup.find(
        'a',
        href='/?order_by=%s.desc' % column_key,
        text=re.compile(re.escape(column_label)),
    )


@patch('dodotable.schema.Schema.environment', new_callable=PropertyMock,
       return_value=DodotableTestEnvironment())
def test_table(environ, fx_session, fx_music):
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
    table_after_search = table.select()
    table_after_search_soup = extract_soup(table_after_search)

    # Must display search result.
    assert table_after_search_soup.find(
        'td',
        text=re.compile(re.escape(fx_music.name))
    )

    # Must not claim empty.
    assert not table_after_search_soup.find(
        'td',
        class_='table-empty-data'
    )

    # Must display search result count.
    result_count = fx_session.query(Music).filter(
        Music.name.ilike(u'%{}%'.format(fx_music.name))
    ).count()
    assert table_after_search_soup.find(
        'div',
        class_='table-information',
        text=re.compile(str(result_count))
    )


class MockCell(Cell):

    def __html__(self):
        return '<td><button>{}</button></td>'.format(self.data)


class MockColumn(Column):

    def __cell__(self, col, row, data, attribute_name, default=None):
        return MockCell(col=col, row=row,
                        data=getattr(data, attribute_name, default))


def test_custom_cell(fx_session, fx_music):
    fx_session.commit()
    table = Table(cls=Music, label='hello', columns=[
        MockColumn(label=u'hello', attr='id', order_by='id.desc')
    ], sqlalchemy_session=fx_session)
    table.select()
    row = table.rows[0]
    row_soup = extract_soup(row)
    cell = row_soup.find('td')
    assert cell
    button = cell.find('button')
    assert button
    assert str(fx_music.id) in button.text


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
