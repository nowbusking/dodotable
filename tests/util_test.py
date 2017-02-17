from six import text_type

from dodotable.util import string_literal


def test_string_literal():
    assert isinstance(string_literal(1), text_type)
    assert isinstance(string_literal(1.1), text_type)
    assert isinstance(string_literal('hello'), text_type)
    assert isinstance(string_literal(u'hello'), text_type)
