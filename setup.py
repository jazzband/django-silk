# -*- coding: utf-8 -*-
"""Define the Django Silk setup."""
import os
from setuptools import setup

try:
    from pypandoc import convert

    def read_md(f):
        return convert(f, 'rst')
except ImportError:
    print("warning: pypandoc module not found, could not convert Markdown to RST")

    def read_md(f):
        return open(f, 'r').read()

README = read_md('README.md')

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='django-silk',
    version='3.0.2',
    packages=['silk'],
    include_package_data=True,
    license='MIT License',
    description='Silky smooth profiling for the Django Framework',
    long_description=README,
    url='https://github.com/jazzband/django-silk',
    author='Michael Ford',
    author_email='mtford@gmail.com',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 1.11',
        'Framework :: Django :: 2.0',
        'Framework :: Django :: 2.1',
        'Framework :: Django :: 2.2',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
    install_requires=[
        'Django>=1.11',
        'Pygments',
        'python-dateutil',
        'requests',
        'sqlparse',
        'Jinja2',
        'autopep8',
        'pytz',
        'gprof2dot>=2017.09.19',
    ]
)
