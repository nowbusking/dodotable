# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup

from dodotable.environment import Environment


def extract_soup(renderable):
    """Convert renderable dodotable schema into BeautifulSoup tag.

    :param renderable: Renderable
    :return: beautifulsoup object of the renderable
    :rtype: :class:`bs4.BeautifulSoup`

    """
    return BeautifulSoup(renderable.__html__(), 'lxml')


class DodotableTestEnvironment(Environment):

    def build_url(self, *args, **kwargs):
        queries = ['{}={}'.format(k, v) for k, v in kwargs.items()]
        return '/?{}'.format('&'.join(sorted(queries)))

    def get_session(self):
        return None
