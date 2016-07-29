#!/usr/bin/env python

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

config = {
    'description': 'deployable_sql',
    'author': 'Dan Cohen',
    'url': 'deltaco.usccreditunion.org',
    'download_url': 'git.usccreditunion.org',
    'author_email': 'dcohen@usccreditunion.org',
    'version': '0.0.12',
    'install_requires': ['pymssql==2.1.3', 'docopt==0.6.2'],
    'packages': ['deployable_sql'],
    'scripts': ['bin/deploy.py'],
    'name': 'deployable_sql'
}

setup(**config)
