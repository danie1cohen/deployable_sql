#!/usr/bin/env python
"""deployable.py

This script allows you to keep SQL Scripts under source control, and manage
SQL views, tables, and stored procedures as if they were deployable code.

Usage:
    deployable.py setup <usr> <db>
    deployable.py <usr> <pwd> <host> <db> [options]
    deployable.py auto [options]

Options:
    -h, --help                      Show this screen.
    -f, --filename=<filename>       A single file to sync.
    --schema=<schema>               Specify a non-standard schema. [default: cu]
    --all                           Rebuild everything.
    --views                         Rebuild only views.
    --test                          Test the connection
"""
import os
import logging
import logging.config
import pickle

from docopt import docopt
import yaml

from deployable_sql.db import PyMSSQLDeployer
from deployable_sql.folders import run_setup
from deployable_sql.central import BASE_DIR


def main():
    """
    Parses arguments and does the doing.
    """
    args = docopt(__doc__)

    if args['setup']:
        run_setup(args['<usr>'], args['<db>'])
        return None

    with open(os.path.join(BASE_DIR, 'logging.yml'), 'rb') as stream:
        logging.config.dictConfig(yaml.load(stream))
    logger = logging.getLogger(__name__)

    if args['auto']:
        usr = os.getenv('DEPLOYABLE_USR')
        pwd = os.getenv('DEPLOYABLE_PWD')
        host = os.getenv('DEPLOYABLE_HOST')
        db = os.getenv('DEPLOYABLE_DB')
        d = PyMSSQLDeployer(
            usr, pwd, host, db, schema=args['--schema'], logger=logger
            )
    else:
        d = PyMSSQLDeployer(
            args['<usr>'], args['<pwd>'], args['<host>'], args['<db>'],
            schema=args['--schema'], logger=logger
            )

    if args['--test']:
        d.test()

    if args['--all'] or args['--views']:
        views = os.path.join('.', 'views')
        d.sync_views(views)

    print('Done!')


if __name__ == "__main__":
    main()
