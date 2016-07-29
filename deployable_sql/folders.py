"""
Folders to set up in the install location.
"""
import os
from subprocess import call


FOLDERS = ['views', 'tables', 'functions', 'stored_procedures', 'permissions']

FILES = [os.path.join('permissions', 'grant_deployable.sql')]

GRANTS = """
USE %(db)s;

GRANT SELECT ON SCHEMA :: dbo TO %(user)s;
GRANT CONTROL ON SCHEMA :: cu TO %(user)s;

GRANT CREATE VIEW TO %(user)s;
GRANT CREATE FUNCTION TO %(user)s;
GRANT CREATE TABLE TO %(user)s;

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
