from contextlib import contextmanager
import functools
import re

from dodotable.environment import Environment
from dodotable.schema import Schema


def removed_spaces(html):
    html = re.sub(r'(>\s+)', r'>', html)
    html = re.sub(r'(\s+<)', r'<', html)
    html = re.sub(r'\n', '', html)
    # remove action
    html = re.sub(r'action=".+" ', '', html)
    return html


def compare_html(actual, expected):
    return removed_spaces(actual) == removed_spaces(expected)


class DodotableTestEnvironment(Environment):

    def build_url(self, *args, **kwargs):
        queries = ['{}={}'.format(k, v) for k, v in kwargs.items()]
        return '/?{}'.format('&'.join(queries))

    def get_session(self):
        return None


@contextmanager
def mock_environment():
    try:
        old = Schema.environment
        Schema.environment = DodotableTestEnvironment()
        yield
    finally:
        Schema.environment = old


def monkey_patch_environment(test):
    def decorate_callable(test):
        @functools.wraps(test)
        def wrapper(*args, **kw):
            with mock_environment():
                return test(*args, **kw)
        return wrapper

    return decorate_callable(test)


pager_html = u'''
<ul class="pager">
    <li>이전</li>
    <li class="first"><span class="selected">1</span></li>
    <li>다음</li>
</ul>
'''
