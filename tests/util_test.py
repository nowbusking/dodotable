from six import text_type

from dodotable.util import string_literal, _get_data


def test__get_data():
    a = type('custom', (), {'c': 'ac', 'd': 'ad'})
    data = type('data', (), {'a': a, 'b': 'b'})
    assert _get_data(data, 'a', None) is a
    assert _get_data(data, 'a.c', None) == 'ac'
    assert _get_data(data, 'a.d', None) == 'ad'
    assert _get_data(data, 'a.b', None) is None
    assert _get_data(data, 'a.b', '') == ''
    assert _get_data(data, 'a.b', 'default') == 'default'
    assert _get_data(data, 'b', None) == 'b'
    assert _get_data(data, 'c', None) is None
    assert _get_data(data, 'c', '') == ''
    assert _get_data(data, 'c', 'default') == 'default'


def test_string_literal():
    assert isinstance(string_literal(1), text_type)
    assert isinstance(string_literal(1.1), text_type)
    assert isinstance(string_literal('hello'), text_type)
    assert isinstance(string_literal(u'hello'), text_type)
