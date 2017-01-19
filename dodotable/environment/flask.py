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

    def get_locale(self):
        # FIXME
        # 현재 도도테이블을 사용하는 모든 Flask 서비스에서 공통적으로 정의되는
        # 로케일 판별 수단이 뭐가 있을지 모르겠어서 일단 임시로 리퀘스트의
        # accept_language를 사용합니다.
        try:
            return request.accept_languages.best_match(['ko', 'jp', 'en'])
        except:
            return 'ko'
