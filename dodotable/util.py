# -*- coding: utf-8 -*-
""":mod:`dodotable.util` --- utilities
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""
import codecs
import gettext
import numbers
import re

from jinja2 import Environment, PackageLoader
import six


__all__ = (
    'camel_to_underscore', 'render', '_get_data',
    'string_literal',
)


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
    default_loader = PackageLoader('dodotable', 'templates')
    loader = extra_environments.get(
        'template_loader',
        default_loader)
    if not loader:
        loader = default_loader
    get_translations = extra_environments.get('get_translations')
    env = Environment(loader=loader,
                      extensions=['jinja2.ext.i18n', 'jinja2.ext.with_'],
                      autoescape=True)
    env.globals.update(extra_environments)
    translations = get_translations() if callable(get_translations) else None
    if translations is None:
        translations = gettext.NullTranslations()
    env.install_gettext_translations(translations)
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


if six.PY2:
    def to_str(x):
        if isinstance(x, six.text_type):
            return x
        if isinstance(x, numbers.Number):
            x = str(x)
        elif x is None:
            x = ''
        return codecs.unicode_escape_decode(x)[0]
    string_literal = to_str
else:
    string_literal = str
