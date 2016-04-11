# -*- coding: utf-8 -*-
import lxml.html.diff
import re
try:
    from urllib import unquote
except ImportError:
    from urllib.parse import unquote

from dodotable.environment import Environment


def removed_spaces(html):
    # 태그 시작과 끝에 빈칸을 삭제합니다.
    html = re.sub(r'(>\s+)', r'>', html)
    html = re.sub(r'(\s+<)', r'<', html)
    # attribute값 근처의 빈칸을 삭제합니다.
    html = re.sub(r'("\s+)', r'" ', html)
    html = re.sub(r'(\s+")', r' "', html)
    # 줄바꿈을 삭제합니다.
    html = re.sub(r'\n', '', html)
    # 셀프클로징을 없앱니다
    html = re.sub(r' \/>', '>', html)
    return html


def html_unquote(html):
    html = unquote(html)
    replacements = [
        ('&amp;', '&'),
        ('&gt;', '>'),
        ('&lt;', '<'),
    ]
    for target, replacement in replacements:
        html = html.replace(target, replacement)
    return html


def compare_html(actual, expected):
    _actual = removed_spaces(actual)
    _expected = removed_spaces(expected)
    diff = html_unquote(lxml.html.diff.htmldiff(_actual, _expected))
    for i, (a, e) in enumerate(zip(_actual, _expected)):
        if a != e:
            print(i)
            break
    assert diff == _actual, _actual[:i]
    return diff == _actual


class DodotableTestEnvironment(Environment):

    def build_url(self, *args, **kwargs):
        queries = ['{}={}'.format(k, v) for k, v in kwargs.items()]
        return '/?{}'.format('&'.join(sorted(queries)))

    def get_session(self):
        return None


pager_html = u'''
<ul class="pager">
  <li class="page-stepper">이전</li>
  <li>
      <ol class="pager-pages">
          <li class="first"><span class="selected">1</span></li>
      </ol>
  </li>
  <li class="page-stepper">다음</li>
</ul>
'''

table_html = u'''
<div class="table-wrap">

    <div class="table-header-wrap">
      <div class="table-header">
        <h5 class="table-title">
          {title}
        </h5>

        <div class="table-filters">
          {filters}
        </div>

        <div class="table-information">
          총 {count}개 {unit_label}이(가) 있습니다.
        </div>
      </div>

    </div>


    <table class="table">

        <thead>
          {columns}
        </thead>

        <tbody>
          {rows}
        </tbody>
    </table>

    <div class="table-footer">
        {pager}
        <div class="limit-view">
        </div>
    </div>
</div>
'''.format
