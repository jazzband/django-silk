import os

from setuptools import find_packages, setup

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='django-silk',
    use_scm_version=True,
    packages=find_packages(exclude=['project*', 'tests*', 'node_modules*']),
    include_package_data=True,
    license='MIT License',
    description='Silky smooth profiling for the Django Framework',
    keywords='django profiling debugging sql n+1 performance monitoring',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/jazzband/django-silk',
    author='Michael Ford',
    author_email='mtford@gmail.com',
    maintainer='Jazzband',
    maintainer_email='jazzband@googlegroups.com',
    project_urls={
        'Source': 'https://github.com/jazzband/django-silk',
        'Bug Tracker': 'https://github.com/jazzband/django-silk/issues',
    },
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 4.2',
        'Framework :: Django :: 5.0',
        'Framework :: Django :: 5.1',
        'Framework :: Django :: 5.2',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
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
        'gprof2dot>=2017.09.19',
    ],
    extras_require={
        'formatting': ['autopep8'],
    },
    python_requires='>=3.10',
    setup_requires=['setuptools_scm'],
)
