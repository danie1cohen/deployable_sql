"""
Folders to set up in the install location.
"""
import os
from subprocess import call
from datetime import datetime

import yaml


FOLDERS = [
    'views', 'tables', 'functions', 'stored_procedures', 'permissions', 'jobs'
    ]

FILES = [os.path.join('permissions', 'grant_deployable.sql')]

GRANTS = """
USE %(db)s;

GRANT SELECT ON SCHEMA :: dbo TO %(user)s;
GRANT CONTROL ON SCHEMA :: cu TO %(user)s;

GRANT CREATE VIEW TO %(user)s;
GRANT CREATE FUNCTION TO %(user)s;
GRANT CREATE TABLE TO %(user)s;
GRANT CREATE PROCEDURE TO %(user)s;

"""

def run_setup(username, db, gitinit=True):
    """Sets up the appropriate folders."""
    for f in FOLDERS:
        if not os.path.exists(f):
            os.mkdir(f)

    with open(os.path.join('permissions', 'grant_deployable.sql'), 'w') as stream:
        stream.write(GRANTS % {'user': username, 'db': db})

    if gitinit: #cover: no pragma
        call('git init', shell=True)

    print('All set!')

def create_job(jobname):
    """
    Creates a basic job from template.
    """
    yml = {
        jobname:
            {
                'steps': [
                    {
                        'step_name': jobname,
                        'command': 'EXEC %s;' % jobname
                    }
                ],
                'schedules': [
                    {
                        'frequency_type': 'weekly',
                        'frequency_interval': 'sunday',
                        'active_start_time': '060000',
                        'active_start_date': datetime.now().strftime('%Y-%m-%d'),
                        'schedule_name': 'weekly'
                    }
                ]
            }
        }
    if not os.path.exists('jobs'):
        os.mkdir('jobs')
    with open(os.path.join('jobs', jobname + '.yml'), 'w') as stream:
        stream.write(yaml.dump(yml, default_flow_style=False))
    return yml
