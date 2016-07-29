#!/usr/bin/env python
"""deployable.py

This script allows you to keep SQL Scripts under source control, and manage
SQL views, tables, and stored procedures as if they were deployable code.

Usage:
    deployable.py setup <usr> <db>
    deployable.py sync <usr> <pwd> <host> <db> [options]
    deployable.py auto [options]
    deployable.py create_job <jobname>

Options:
    -h, --help                      Show this screen.
    -f, --filename=<filename>       A single file to sync.
    --schema=<schema>               Specify a non-standard schema. [default: cu]
    --all                           Rebuild everything.
    --views                         Rebuild only views.
    --jobs                          Rebuild the jobs folder.
    --test                          Test the connection.
"""
import os
import logging
import logging.config

from docopt import docopt

from deployable_sql.db import PyMSSQLDeployer
from deployable_sql.folders import run_setup, create_job


LOGGERS = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'simple': {
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            }
        },
    'handlers': {
        'console_handler': {
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
            'stream': 'ext://sys.stdout',
            'level': 'DEBUG'
            }
        },
    'root': {
        'handlers': ['console_handler'],
        'level': 'DEBUG'
        },
    'loggers': {
        'default': {
            'handlers': ['console_handler'],
            'propagate': False,
            'level': 'ERROR'
            }
        }
    }


def main():
    """
    Parses arguments and does the doing.
    """
    args = docopt(__doc__)

    if args['setup']:
        run_setup(args['<usr>'], args['<db>'])
        return None
    elif args['create_job']:
        create_job(args['<jobname>'])
        return None

    logging.config.dictConfig(LOGGERS)
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
    views = os.path.join('.', 'views')
    tables = os.path.join('.', 'tables')
    functions = os.path.join('.', 'functions')
    stored_procedures = os.path.join('.', 'stored_procedures')
    jobs = os.path.join('.', 'jobs')
    if args['--test']:
        d.test()

    if args['--all']:
        d.sync_folder(views)
        d.sync_folder(jobs)
        #d.sync_folder(functions)
        #d.sync_folder(stored_procedures)
    elif args['--views']:
        d.sync_folder(views)
    elif args['--jobs']:
        d.sync_folder(jobs)
    elif args['--filename']:
        d.sync_file(args['--filename'])


    print('Done!')


if __name__ == "__main__":
    main()
