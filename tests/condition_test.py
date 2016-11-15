# -*- coding: utf-8 -*-
from pytest import mark

from dodotable.condition import (Ilike, IlikeSet, SelectFilter, IlikeAlias,
                                 create_search_name)
from dodotable.schema import Table, Column
from dodotable.util import camel_to_underscore
from mock import PropertyMock, patch

from .entities import Music, Tag
from .helper import (DodotableTestEnvironment, compare_html, pager_html,
                     table_html)


@patch('dodotable.schema.Schema.environment', new_callable=PropertyMock,
       return_value=DodotableTestEnvironment())
def test_ilike(environ, fx_session, fx_music):
    word = fx_music.name
    name = create_search_name(camel_to_underscore(Music.__name__))
    payload = dict([
        (name['type'], u'name'),
        (name['word'], word)
    ])
    table_label = u'test'
    table = Table(cls=Music, label=table_label, columns=[
        Column(attr='id', label=u'id', order_by='id.desc'),
        Column(attr='name', label=u'이름', filters=[
            Ilike(Music, 'name', payload)
        ]),
    ], sqlalchemy_session=fx_session)
    ilike_set = IlikeSet(table=table,
                         request_args=payload)
    table.add_filter(ilike_set)
    search_html = u'''
    <form method="GET" action="/?search_music.type=name&search_music.word={1.name}" class="search-filter-wrap">
        <select name="{0[type]}" class="form-control search-filter">
            <option value="name">
                이름
            </option>
        </select>

        <input type="text" name="{0[word]}"
         value="{1.name}" class="form-control search-input" />

        <input type="hidden" name="{0[word]}"
         value="{1.name}" />
    </form>
    '''.format(name, fx_music)  # noqa
    q = fx_session.query(Music) \
                  .filter(Music.name.ilike(u'%{}%'.format(word)))
    music = q.one()
    expected_rows = u'''
    <tr>
      <td>{id}</td>
      <td>{name}</td>
    </tr>
    '''.format(id=music.id, name=music.name)
    column_html = u'''<tr><th class="order-desc ">
      <a href="/?order_by=id.asc">id</a>
    </th>
    <th class="order-none ">
      <a href="/?order_by=name.desc">이름</a>
    </th>
    </tr>
    '''
    actual_ilike = ilike_set.__html__()
    assert compare_html(actual_ilike, search_html)
    table = table.select(offset=0, limit=10)
    actual_table = table.__html__()
    expected_table = table_html(count=q.count(), rows=expected_rows,
                                filters=search_html, columns=column_html,
                                title=table_label, pager=pager_html,
                                unit_label='row')
    assert compare_html(actual_table, expected_table)


@mark.parametrize('t', ['genre', 'country'])
def test_select_filter(fx_tags, fx_session, t):
    select_filter = SelectFilter(
        Tag,
        't',
        choices=[
            {'name': 'genre', 'description': ''},
            {'name': 'country', 'description': ''},
        ],
        arguments={
            'select.t': t
        }
    )
    tag_table = Table(Tag, 'a', columns=[
        Column('t', 't'),
    ], sqlalchemy_session=fx_session)
    tag_table.add_filter(select_filter)
    tag_table = tag_table.select(0, 100)
    xs = [r[0].data for r in tag_table.rows]
    assert all([x == t for x in xs])


@mark.parametrize('t', ['genre', 'country'])
def test_ilike_alias(fx_tags, t, fx_session):
    alias_type = Tag.t.label('type')
    tag = fx_session.query(Tag) \
                    .filter(IlikeAlias('tag_type', alias_type,
                                       {'select.tag_type': t}).__query__())
    assert all([tg.t == t for tg in tag])
