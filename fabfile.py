#!/usr/bin/env python
"""
This fab file is for deploying new code and remotely managing the machines code
is installed on.
"""
from __future__ import print_function
import os
from datetime import datetime

from fabric.api import run, env, cd, prefix, put, sudo, local


env.host_string = 'administrator@gelsons'
env.user = 'administrator'
env.key_filename = 'U:\\.ssh\\id_rsa'

data = {
    'install_path': '/opt/deployable_sql',
    'current': '/opt/deployable_sql/current',
    'repo': 'git@git.usccreditunion.org:cu/deployable_sql.git',
    'build': datetime.now().strftime('%Y%m%d%H%M%S'),
    'settings': 'settings.p',
    'user': env.user
}


def deploy():
    """Deploys new code and handles the commands that must follow"""
    with cd('%(install_path)s' % data):
        run('git clone %(repo)s %(build)s' % data)
        #run('cp current/%(settings)s %(build)s/%(settings)s' % data)
        with cd('%(build)s' % data), prefix('workon sql'):
            run('pip install -U pip')
            run('pip install -r requirements.txt')
            run('nosetests -v')
            # if tests pass, change symlink
            remove = 'rm -rf %(current)s' % data
            replace = 'ln -sfn %(install_path)s/%(build)s %(current)s' % data
            run(remove + ' && ' + replace)
            run('pip uninstall -y deployable_sql')
            run('pip install .')
    increment_version()

def create():
    """
    Does initial folder setup.
    """
    #local('ssh-copy-id -i %s %s' % (env.key_filename, env.host_string))
    #put('%(settings)s' % data)
    #sudo('chmod 700 %(settings)s' % data)
    sudo('mkdir %(install_path)s' % data)
    sudo('chown -R %(user)s:%(user)s %(install_path)s' % data)
    with cd('%(install_path)s' % data):
        run('mkdir current')
        run('mkvirtualenv sql')
        #run('mv ~/%(settings)s %(current)s/%(settings)s' % data)
    # set up log dir
    sudo('mkdir /var/log/deployable_sql')
    sudo('chown -R %(user)s:%(user)s /var/log/deployable_sql' % data)
    deploy()

def oneoff():
    """Run deployable_sql as a one off process."""
    with cd('%(current)s' % data), prefix('workon sql'):
        run('python bin/deploy.py auto --all')

def increment_version():
    """Increments setup.py to the next version."""
    if os.path.exists('setup.py'):
        with open('setup.py', 'r') as infile:
            lines = infile.readlines()
        with open('setup.py', 'w') as outfile:
            for line in lines:
                if 'version' in line:
                    line = increment_last(line)
                outfile.write(line)
    else:
        print('No setup.py file found!')

def increment_last(line):
    """Takes the setup.py version line and returns an incremented one."""
    key, val = line.split(':')
    val = val.replace("'", '').replace('"', '').replace(',', '')
    vals = [int(v.strip()) for v in val.split('.')]
    vals[-1] = vals[-1] + 1
    version_plus = '.'.join([str(val) for val in vals])
    print('Incrementing setup.py to version: %s' % version_plus)
    return "%s: '%s',\n" % (key, version_plus)

def deployed_version():
    """
    Return the version of the current deployed code.
    """
    run('cat %(current)s/setup.py | grep -i version' % data)

def uname():
    """
    Gets the uname from the remote machine.
    """
    run('uname -s')

def chmod_settings():
    """Restrict file access for settings file."""
    with cd(data['current']):
        sudo('chmod 700 %(settings)s' % data)
