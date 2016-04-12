# -*- coding: utf-8 -*-
""":mod:`dodotable.exc` --- Errors
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""
__all__ = 'BadChoice',


class BadChoice(Exception):
    """예상하지 못한 선택지를 골랐을 때 발생합니다."""
