# -*- coding: utf-8 -*-
"""Define the Django Silk setup."""
import os
from setuptools import setup

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

README = open('README.md', 'rb').read().decode("UTF-8")

setup(
    name='django-silk',
    version='4.0.0',
    packages=['silk'],
    include_package_data=True,
    license='MIT License',
    description='Silky smooth profiling for the Django Framework',
    long_description=README,
    long_description_content_type='text/markdown',
    url='https://github.com/jazzband/django-silk',
    author='Michael Ford',
    author_email='mtford@gmail.com',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 2.2',
        'Framework :: Django :: 3.0',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
    install_requires=[
        'Django>=2.2',
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
