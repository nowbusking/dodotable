import six

from dodotable.util import string_literal


def test_string_literal():
    assert isinstance(string_literal(1), six.text_type)
    assert isinstance(string_literal(1L), six.text_type)
    assert isinstance(string_literal(1.1), six.text_type)
    assert isinstance(string_literal('hello'), six.text_type)
    assert isinstance(string_literal(u'hello'), six.text_type)
