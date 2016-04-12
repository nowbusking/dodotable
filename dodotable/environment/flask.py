""":mod:`dodotable.environment.flask` --- Flask environment
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""
from __future__ import absolute_import
from flask import request

from . import Environment


__all__ = 'FlaskEnvironment',


class FlaskEnvironment(Environment):
    """Build table with :mod:`flask`"""

    def build_url(self, **kwargs):
        arg = request.args.copy()
        view_args = request.view_args
        arg.update(view_args)
        for attr in kwargs.keys():
            if attr in arg:
                arg.pop(attr)
        arg.update(kwargs.items())
        rule = request.url_rule
        result = rule.build(arg)
        return result[1]

    def get_session(self):
        ctx = request._get_current_object()
        try:
            session = ctx._current_session
        except AttributeError:
            return None
        else:
            return session
