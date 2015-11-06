import ast
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
                    node.targets[0].id == '__version__'):
                version = ast.literal_eval(node.value)
        if isinstance(version, tuple):
            version = '.'.join([str(x) for x in version])
        return version


tests_require = [
    'pytest >= 2.7.0',
    'tox >= 2.1.1',
]
install_requires = [
    'setuptools',
    'flask',
    'jinja2',
    'SQLAlchemy',
]
extras_require = [
    'import-order',
    'flake8'
]


setup(
    name='dodotable',
    version=get_version(),
    description='dodotable',
    long_description=readme(),
    license='Public Domain',
    author='Kang Hyojun',
    author_email='ed' '@' 'spoqa.com',
    packages=find_packages(),
    install_requires=install_requires,
    extras_require={
        'tests': tests_require,
        'extras': extras_require
    },
    tests_require=tests_require,
    classifiers=[]
)
