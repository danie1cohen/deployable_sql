#!/usr/bin/env python
"""deploy_sql.py

This script allows you to keep SQL Scripts under source control, and manage
SQL views, tables, and stored procedures as if they were deployable code.

Usage:
    deploy_sql.py setup <usr> <db>
    deploy_sql.py [options]
    deploy_sql.py <usr> <pwd> <host> <db> [options]
    deploy_sql.py create_job <jobname> [--recurrence=(daily|weekly)]

Options:
    -h, --help                      Show this screen.
    -f, --filename=<filename>       A single file to sync.
    --schema=<schema>               Specify a non-standard schema. [default: cu]
    --test                          Test the connection.
    --all                           Rebuild everything.
    --functions                     Rebuild the functions folder.
    --jobs                          Rebuild the jobs folder.
    --sps                           Rebuild stored procedures.
    --views                         Rebuild only views.
"""
import os
import logging
import logging.config

from docopt import docopt
import yaml

from deployable_sql.deployers.pymssql import PyMSSQLDeployer
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


def get_credentials(args):
    """
    Check a config file, environment variables, or the command line arguments
    and return credentials for the deployer.

    The order of precence is same as above.
    """
    config_path = os.path.expanduser('~/.deploy_sql.yml')
    if os.path.exists(config_path):
        with open(config_path, 'rb') as stream:
            config = yaml.load(stream)
    else:
        config = {}

    usr = config.get('usr', os.getenv('DEPLOYABLE_USR', args['<usr>']))
    pwd = config.get('pwd', os.getenv('DEPLOYABLE_PWD', args['<pwd>']))
    host = config.get('host', os.getenv('DEPLOYABLE_HOST', args['<host>']))
    db = config.get('db', os.getenv('DEPLOYABLE_DB', args['<db>']))

    return usr, pwd, host, db


def main():
    """
    Parses arguments and does the doing.
    """
    args = docopt(__doc__)

    if args['setup']:
        run_setup(args['<usr>'], args['<db>'])
        return None
    elif args['create_job']:
        create_job(args['<jobname>'], recurrence=args['--recurrence'])
        return None

    logging.config.dictConfig(LOGGERS)
    logger = logging.getLogger(__name__)

    usr, pwd, host, db = get_credentials(args)

    d = PyMSSQLDeployer(
        usr, pwd, host, db, schema=args['--schema']
    )

    views = os.path.join('.', 'views')
    tables = os.path.join('.', 'tables')
    functions = os.path.join('.', 'functions')
    stored_procedures = os.path.join('.', 'stored_procedures')
    jobs = os.path.join('.', 'jobs')

    if args['--test']:
        d.test()
    elif args['--all']:
        d.sync_folder(views)
        d.sync_folder(jobs)
        d.sync_folder(functions)
        d.sync_folder(stored_procedures)
    elif args['--filename']:
        d.sync_file(args['--filename'])
    elif args['--functions']:
        d.sync_folder(functions)
    elif args['--jobs']:
        d.sync_folder(jobs)
    elif args['--sps']:
        d.sync_folder(stored_procedures)
    elif args['--views']:
        d.sync_folder(views)

    print('Done!')


if __name__ == "__main__":
    main()
