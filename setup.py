#!/usr/bin/env python

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

config = {
    'description': 'deployable_sql',
    'author': 'Dan Cohen',
    'url': 'https://github.com/danie1cohen/deployable_sql',
    'download_url': 'https://github.com/danie1cohen/deployable_sql/archive/master.zip',
    'author_email': 'daniel.o.cohen@gmail.com',
    'version': '1.0.0',
    'install_requires': [
        'pymssql==2.1.3',
        'docopt==0.6.2',
        'python-dateutil==2.5.3',
        'PyYAML==3.11',
        'SQLAlchemy==1.0.14'
    ],
    'packages': ['deployable_sql'],
    'scripts': ['bin/deploy_sql.py'],
    'name': 'deployable_sql'
}

setup(**config)
