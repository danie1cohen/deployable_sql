#!/usr/bin/env python

try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup, find_packages

config = {
    'description': 'deployable_sql',
    'author': 'Dan Cohen',
    'url': 'https://github.com/danie1cohen/deployable_sql',
    'download_url': 'https://github.com/danie1cohen/deployable_sql/archive/master.zip',
    'author_email': '8837255+danie1cohen@users.noreply.github.com',
    'version': '1.0.1',
    'install_requires': [
        'pymssql',
        'docopt',
        'python-dateutil',
        'PyYAML'
    ],
    'packages': find_packages(),
    'scripts': ['bin/deploy_sql.py'],
    'name': 'deployable_sql'
}

setup(**config)
