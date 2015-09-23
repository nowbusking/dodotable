""":mod:`dodotable.util` --- utility
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""
import codecs
import re
import sys

from jinja2 import PackageLoader
from jinja2 import Environment

__all__ = 'camel_to_underscore', 'render', '_get_data'


#: (:class:`_sre.SRE_Pattern`) 첫번째 대문자를 찾습니다.
first_cap_re = re.compile('(.)([A-Z][a-z]+)')
#: (:class:`_sre.SRE_Pattern`) 단어 중에 첫번째가아닌 모든 대문자를 찾습니다.
all_cap_re = re.compile('([a-z0-9])([A-Z])')


def camel_to_underscore(name):
    """CamelCase로 주어진 ``name``\ 을 underscore_with_lower_case로 변환합니다

    .. code-block:: python

       >>> camel_to_underscore('SomePythonClass')
       'some_python_class'

    :param str name: name to convert
    :return: converted name
    :rtype: :class:`str`

    """
    s1 = first_cap_re.sub(r'\1_\2', name)
    return all_cap_re.sub(r'\1_\2', s1).lower()


def render(template_name, extra_environments={}, **kwargs):
    """주어진 템플릿을 jinja로 렌더링합니다

    :param template_name:
    :return:

    """
    env = Environment(loader=PackageLoader('dodotable', 'templates'),
                      extensions=('jinja2.ext.with_',))
    env.globals.update(extra_environments)
    template = env.get_template(template_name)
    return template.render(**kwargs)


def _get_data(data, attribute_name, default):
    name_chain = attribute_name.split('.')

    def __data__(_data, name_chain):
        if len(name_chain) > 0:
            try:
                return __data__(getattr(_data, name_chain[0]),
                                name_chain[1:])
            except AttributeError:
                return u''
        return _data

    return __data__(data, name_chain) or default


if sys.version_info < (3,):
    string_literal = lambda x: codecs.unicode_escape_decode(x)[0]
else:
    string_literal = str
