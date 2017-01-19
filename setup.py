import ast
import sys
from setuptools import find_packages, setup


def readme():
    try:
        f = open('README.rst')
    except IOError:
        return
    try:
        return f.read()
    finally:
        f.close()


def get_version():
    filename = 'dodotable/__init__.py'
    with open(filename, 'r') as f:
        tree = ast.parse(f.read(), filename)
        for node in tree.body:
            if (isinstance(node, ast.Assign) and
                    node.targets[0].id == '__version_info__'):
                version = '.'.join(
                    str(x) for x in ast.literal_eval(node.value)
                )
                return version
        else:
            raise ValueError('could not find __version_info__')


tests_require = [
    'lxml',
    'pytest >= 2.7.0',
    'tox >= 2.1.1',
    'import-order',
    'flake8',
]
install_requires = [
    'setuptools',
    'Flask',
    'Jinja2',
    'SQLAlchemy',
    'six >= 1.10.0, < 2.0.0',
]


def get_install_requirements(requires):
    install_requires = requires[:]
    if 'bdist_wheel' not in sys.argv and sys.version_info < (3, 4):
        install_requires.append('mock')
    return install_requires


setup(
    name='dodotable',
    version=get_version(),
    description='dodotable',
    long_description=readme(),
    url='https://github.com/spoqa/dodotable',
    license='MIT',
    author='Kang Hyojun',
    author_email='ed' '@' 'spoqa.com',
    packages=find_packages(exclude=['tests']),
    package_data={
        'dodotable': ['locale/*/LC_MESSAGES/*.mo', 'templates/*.html'],
    },
    install_requires=get_install_requirements(install_requires),
    extras_require={
        'tests': tests_require,
    },
    setup_requires=['Babel'],
    tests_require=tests_require,
    message_extractors={
        'dodotable': [('**.py', 'python', None)],
        'dodotable/templates': [
            ('**.html', 'jinja2', {
                'encoding': 'utf-8',
                'extensions': 'jinja2.ext.autoescape,jinja2.ext.with_',  # noqa
                'silent': 'false',
            }),
        ],
    },
    classifiers=[]
)
