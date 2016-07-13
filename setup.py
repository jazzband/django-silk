import os
from setuptools import setup

README = open('README.rst','r').read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='django-silk',
    version='0.6.0',
    packages=['silk'],
    include_package_data=True,
    license='MIT License',
    description='Silky smooth profiling for the Django Framework',
    long_description=README,
    url='http://www.mtford.co.uk/projects/silk/',
    author='Michael Ford',
    author_email='mtford@gmail.com',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
    install_requires= [
        'Django',
        'Pygments',
        'python-dateutil',
        'requests',
        'sqlparse',
        'Jinja2',
        'autopep8',
        'pytz'
    ]
)
