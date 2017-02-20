# -*- coding: utf-8 -*-
import re

from mock import PropertyMock, patch
from pytest import mark

from .entities import Music, Tag
from .helper import DodotableTestEnvironment, extract_soup
from dodotable.condition import (Ilike, IlikeSet, IlikeAlias, SelectFilter,
                                 create_search_name)
from dodotable.schema import Column, Table
from dodotable.util import camel_to_underscore


@patch('dodotable.schema.Schema.environment', new_callable=PropertyMock,
       return_value=DodotableTestEnvironment())
def test_ilike(environ, fx_session, fx_music):
    """ Test all ilike related objects """

    search_name = create_search_name(camel_to_underscore(Music.__name__))
    payload = dict([
        (search_name['type'], u'name'),
        (search_name['word'], fx_music.name)
    ])
    table_label = u'test'
    table = Table(cls=Music, label=table_label, columns=[
        Column(attr='id', label=u'id', order_by='id.desc'),
        Column(attr='name', label=u'이름', filters=[
            Ilike(Music, 'name', payload)
        ]),
    ], sqlalchemy_session=fx_session)

    ilike_set = IlikeSet(table=table, request_args=payload)
    ilike_set_soup = extract_soup(ilike_set)

    # Must have input field with the search query.
    assert ilike_set_soup.find(
        'input',
        {
            'type': 'text',
            'name': search_name['word'],
            'value': fx_music.name,
        }
    )

    # Must have hidden field with the search query.
    assert ilike_set_soup.find(
        'input',
        {
            'type': 'hidden',
            'name': search_name['word'],
            'value': fx_music.name,
        }
    )

    table.add_filter(ilike_set)
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


@mark.parametrize('t', ['genre', 'country'])
def test_select_filter(fx_tags, fx_session, t):
    select_filter = SelectFilter(
        Tag,
        't',
        choices=[
            {'name': 'genre', 'description': ''},
            {'name': 'country', 'description': ''},
        ],
        request_args={
            'select.t': t
        }
    )
    tag_table = Table(Tag, 'a', columns=[
        Column('t', 't'),
    ], sqlalchemy_session=fx_session)
    tag_table.add_filter(select_filter)
    tag_table = tag_table.select()
    xs = [r[0].data for r in tag_table.rows]
    assert all([x == t for x in xs])


@mark.parametrize('t', ['genre', 'country'])
def test_ilike_alias(fx_tags, t, fx_session):
    alias_type = Tag.t.label('type')
    tag = fx_session.query(Tag) \
                    .filter(IlikeAlias('tag_type', alias_type,
                                       {'select.tag_type': t}).__query__())
    assert all([tg.t == t for tg in tag])
