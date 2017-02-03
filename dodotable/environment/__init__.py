# -*- coding: utf-8 -*-
""":mod:`dodotable.environment` --- Environment for dodotable
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Customize your table
====================

Dodotable has :class:`dodotable.environment.Environment` to render data
to template and get a instance of :class:`sqlalchemy.orm.session.Session` to
requeset a query to database.

Usually :class:`dodotable.environment.Environment` used in
:class:`dodotable.schema.Schema`. :attr:`dodotable.schema.Schema.environment`
generate template loader and define custom function to
Jinja's environment to call a functions in template.

So, you have to inherit environment class and implement some methods,

- :meth:`dodotable.environment.Environment.template_loader`
- :meth:`dodotable.environment.Environment.build_url`
- :meth:`dodotable.environment.Environment.get_session`

A good example is :class:`dodotable.environment.flask.FlaskEnvironment`.
more examples are in it.

"""
import gettext
import os.path

__all__ = 'Environment',


class Environment(object):
    """Top-level environment class, every environment class implemented by
    inherit this class.

    :param locale_selector: a locale returning nullary function for selection
                            of the right translation.
                            the type of a return value can be :class:`str`
                            or :class:`babel.core.Locale` as well.
                            if it's omitted or a return value is :const:`None`
                            English is shown.
    :type locale_selector: :class:`collections.abc.Callable`

    """

    #: (:class:`tuple`) methods that
    __env_methods__ = 'get_session',

    def __init__(self, locale_selector=None):
        if not (locale_selector is None or callable(locale_selector)):
            raise TypeError('locale_selector must be callable, not ' +
                            repr(locale_selector))
        self.get_locale = locale_selector

    @property
    def template_loader(self):
        """Get custom template loader

        :return: jinja template loader
        :rtype: :class:`jinja2.loaders.BaseLoader`

        """
        return None

    def build_url(self, *args, **kwargs):
        raise NotImplementedError()

    def get_session(self):
        raise NotImplementedError()

    def get_translations(self):
        if self.get_locale is None:
            return None
        locale = self.get_locale()
        if locale is None:
            return None
        elif not isinstance(locale, str):
            # locale might be an instance of babel.core.Locale
            locale = str(locale)
        if '_' in locale or '-' in locale:
            # If the locale has territory (e.g. 'ko_KR')
            # we can search the proper match (e.g. ko_KR) and then
            # the non-territory match (e.g. ko) as a fallback.
            locale = locale.replace('-', '_')
            locales = [locale, locale[:locale.index('_')]]
        else:
            locales = [locale]
        return gettext.translation(
            'dodotable',
            os.path.join(os.path.dirname(__file__), '..', 'locale'),
            fallback=True,
            codeset='utf-8',
            languages=locales
        )

    def isinstance(self, instance, cls):
        if not isinstance(cls, type):
            try:
                name = cls.split(':')
                _mod = __import__(name[0], globals(), locals(), [name[1]], 0)
                mod = getattr(_mod, name[1])
            except (ImportError, IndexError):
                return False
        else:
            mod = cls
        return isinstance(instance, mod)

    def __dict__(self):
        env = {}
        for attribute in dir(self):
            if not (attribute.startswith('__') or
                    attribute in self.__env_methods__):
                env.update({attribute: getattr(self, attribute)})
        return env
