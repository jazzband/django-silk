import os

from setuptools import setup

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='django-silk',
    use_scm_version=True,
    packages=['silk'],
    include_package_data=True,
    license='MIT License',
    description='Silky smooth profiling for the Django Framework',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/jazzband/django-silk',
    author='Michael Ford',
    author_email='mtford@gmail.com',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 4.2',
        'Framework :: Django :: 5.0',
        'Framework :: Django :: 5.1',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: 3.13',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
    install_requires=[
        'Django>=4.2',
        'sqlparse',
        'autopep8',
        'gprof2dot>=2017.09.19',
    ],
    python_requires='>=3.8',
    setup_requires=['setuptools_scm'],
)
