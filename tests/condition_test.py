# -*- coding: utf-8 -*-
from pytest import mark

from dodotable.condition import Ilike, IlikeSet, SelectFilter, IlikeAlias, \
    create_search_name
from dodotable.schema import Table, Column
from dodotable.util import camel_to_underscore

from.entities import Music, Tag
from .helper import compare_html, monkey_patch_environment, pager_html


@monkey_patch_environment
def test_ilike(fx_session, fx_music):
    word = fx_music.name
    name = create_search_name(camel_to_underscore(Music.__name__))
    payload = dict([
        (name['type'], u'name'),
        (name['word'], word)
    ])
    table = Table(cls=Music, label=u'test', columns=[
        Column(attr='id', label=u'id', order_by='id.desc'),
        Column(attr='name', label=u'이름', filters=[
            Ilike(Music, 'name', payload)
        ]),
    ], sqlalchemy_session=fx_session)
    ilike_set = IlikeSet(table=table,
                         request_args=payload)
    table.add_filter(ilike_set)
    search_html = u'''
    <form method="GET" action="a" class="ilike-set">
        <select name="{0[type]}">
            <option value="name">
                이름
            </option>
        </select>

        <input type="text" name="{0[word]}"
         value="{1}" />

        <input type="hidden" name="{0[word]}"
         value="{1}" />

        <button type="submit" class="btn btn-default">
            검색
        </button>
    </form>
    '''.format(name, fx_music.name)
    actual = ilike_set.__html__()
    assert compare_html(actual, search_html)
    q = fx_session.query(Music) \
                  .filter(Music.name.ilike(u'%{}%'.format(word)))
    music = q.one()
    expected_rows = u'''
    <tr>
      <td>{id}</td>
      <td>{name}</td>
    </tr>
    '''.format(id=music.id, name=music.name)
    expected = u'''
    <div class="card-wrap dodotable-wrap">
    <p>
      총 {count}개
    </p>

    <div class="filters">
    {search_html}
    </div>

        <table class="table-hover table form-inline dodotable">
            <caption>
              test
            </caption>

            <thead>
                <tr>
                    <th class="order-desc">
                        <a href="/?order_by=id.asc">id</a>
                    </th>
                    <th class="order-none">
                        <a href="/?order_by=name.desc">이름</a>
                    </th>
                </tr>
            </thead>

            <tbody>
              {rows}
            </tbody>
        </table>


        {pager}
    </div>
    '''.format(count=q.count(), rows=expected_rows,
               search_html=search_html, pager=pager_html)
    table = table.select(offset=0, limit=10)
    actual = table.__html__()
    assert compare_html(actual, expected)


@mark.parametrize('t', ['genre', 'country'])
@monkey_patch_environment
def test_select_filter(fx_tags, t, fx_session):
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
