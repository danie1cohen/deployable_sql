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

USE msdb;
GRANT SELECT ON SCHEMA :: dbo TO %(user)s;
GRANT EXECUTE ON OBJECT :: dbo.sp_delete_job TO %(user)s;
GRANT EXECUTE ON OBJECT :: dbo.sp_add_job TO %(user)s;
GRANT EXECUTE ON OBJECT :: dbo.sp_add_jobstep TO %(user)s;
GRANT EXECUTE ON OBJECT :: dbo.sp_add_jobschedule TO %(user)s;
GRANT EXECUTE ON OBJECT :: dbo.sp_add_alert TO %(user)s;
GRANT EXECUTE ON OBJECT :: dbo.sp_add_jobserver TO %(user)s;
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

def create_job(jobname, recurrence='weekly'):
    """
    Creates a basic job from template.
    """
    schedules = {
        'weekly': {
            'freq_type': 'weekly',
            'freq_interval': 'sunday',
            'freq_recurrence_factor': 1,
            'active_start_time': '060000',
            'active_start_date': datetime.now().strftime('%Y-%m-%d'),
            'name': 'weekly'
        },
        'daily': {
            'freq_type': 'daily',
            'freq_interval': 1,
            'active_start_time': '060000',
            'active_start_date': datetime.now().strftime('%Y-%m-%d'),
            'name': 'daily'
        }
    }
    yml = {
        jobname: {
            'steps': [{
                'step_name': jobname,
                'command': "N'EXEC %s;'" % jobname,
                'database_name': 'master'
            }],
            'schedules': [schedules[recurrence]]
        }
    }
    if not os.path.exists('jobs'):
        os.mkdir('jobs')

    with open(os.path.join('jobs', jobname + '.yml'), 'w') as stream:
        stream.write(yaml.dump(yml, default_flow_style=False))

    return yml
