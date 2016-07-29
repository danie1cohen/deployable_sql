"""
Class that interacts with the database.
"""
# pylint: disable=abstract-method
import os
from datetime import datetime
from collections import OrderedDict

import pymssql
from sqlalchemy import create_engine, text
from dateutil.parser import parse

import yaml

from .exc import IllegalPathError



TSQL_FREQ_TYPES = {
    'once': 1,
    'daily': 4,
    'weekly': 8,
    'monthly': 16,
    'monthly_relative': 32,
    'on_agent_start': 64,
    'idle': 128
}

TSQL_FREQ_INTS = {
    'sunday': 1,
    'monday': 2,
    'tuesday': 4,
    'wednesday': 8,
    'thursday': 16,
    'friday': 32,
    'saturday': 64
}


class BaseDeployer(object):
    """Base class for SQL Deployers."""
    def __init__(self, schema="cu", logger=None):
        self.schema = schema
        self.logger = logger

    def sync_function(self, path):
        """Syncs a function."""
        raise NotImplementedError

    def sync_permission(self, path):
        """Syncs a permission."""
        raise NotImplementedError

    def sync_stored_procedure(self, path):
        """Syncs an SP."""
        raise NotImplementedError

    def sync_table(self, path):
        """Syncs a table."""
        raise NotImplementedError

    def sync_view(self, path):
        """Syncs a view."""
        raise NotImplementedError

    def sync_job(self, path):
        """Syncs a job, step, schedule."""
        raise NotImplementedError

    def sync_file(self, path):
        """Syncs a file of not yet determined type."""
        path_mappings = {
            'functions': self.sync_function,
            'permissions': self.sync_permission,
            'stored_procedures': self.sync_stored_procedure,
            'tables': self.sync_table,
            'views': self.sync_view,
            'jobs': self.sync_job,

        }
        if os.path.sep in path:
            if path.startswith('.'): path = path.split(os.path.sep, 1)[-1]
            # if full path is provided, just decide on the right function
            segs = path.split(os.path.sep)
            if len(segs) != 2:
                raise IllegalPathError(path)
            return path_mappings[segs[0]](path)
        else:
            # if partial path is provided, find the right folder
            for root, _, files in os.walk('.'):
                if '.git' in root:
                    continue
                for f in files:
                    if path == f:
                        clean_root = root.split(os.path.sep)[-1]
                        full_path = os.path.join(clean_root, f)
                        return path_mappings[clean_root](full_path)
        raise IllegalPathError(path)

    def _parse_path(self, path):
        """
        Breaks the path up into its important elements and returns them as a
        tuple:
        """
        self.logger.debug('path: %s', path)

        folder = None
        if os.path.sep in path:
            segs = path.split(os.path.sep)
            if len(segs) != 2:
                raise IllegalPathError
            else:
                folder, filename = segs
        basename, ext = os.path.splitext(os.path.basename(path))
        self.logger.debug('parts: (%s, %s, %s)', folder, basename, ext)

        schema_dot_obj = self._schema_path(basename)
        self.logger.debug('schema.obj: %s', schema_dot_obj)

        # read sql from file
        with open(path, 'r') as stream:
            sql = stream.read()
        self.logger.debug('read sql: %s', sql[:140].replace('\n', ''))
        return schema_dot_obj, sql, folder, filename, basename

    def sync_folder(self, folder):
        """
        Syncs all the views in a given folder (that wend with ext .sql).
        """
        self.logger.debug('Looking for files in: %s', folder)
        for sql in os.listdir(folder):
            self.sync_file(os.path.join(folder, sql))

class SqlAlchemyDeployer(BaseDeployer):
    """A deployer that uses sql alchemy conn strings."""
    def __init__(self, conn_string, **kwargs):
        super(SqlAlchemyDeployer, self).__init__(**kwargs)
        self.engine = create_engine(conn_string)

    def _exec(self, sql):
        """Execute a statement."""
        result = self.engine.execute(text(sql))
        self.logger.debug(result.fetchall())

    def test(self):
        """Run a quick test to see if this even works."""
        self._exec('SELECT * FROM INFORMATION_SCHEMA')


class PyMSSQLDeployer(BaseDeployer):
    """Class used to deploy source controlled SQL files to datbase"""
    def __init__(self, usr, pwd, host, db, **kwargs):
        """Creates an engine connection."""
        super(PyMSSQLDeployer, self).__init__(**kwargs)
        self.conn = pymssql.connect(host, usr, pwd, db)
        self.conn.autocommit(True)
        self.cursor = self.conn.cursor()

    def sync_view(self, path):
        """Drops the view if it already exists, then and recreates it."""
        schema_dot_obj, sql = self._parse_path(path)[:2]
        self.logger.debug('Syncing view: %s', schema_dot_obj)
        drop_sql = _if_drop(schema_dot_obj)
        # remove any ORDER BY statements
        sql = '\n'.join([line for line in sql.split('\n')
                         if 'ORDER BY' not in line])
        build_sql = "CREATE VIEW %s AS \n%s;" % (schema_dot_obj, sql)
        self._exec(drop_sql)
        self._exec(build_sql)
        #self._exec('SELECT TOP 1 * FROM %s' % schema_dot_obj)

    def sync_function(self, path):
        """Syncs a function."""
        schema_dot_obj, sql = self._parse_path(path)[:2]
        self.logger.debug('Syncing function: %s', schema_dot_obj)
        drop_sql = _if_drop(schema_dot_obj, object_type='FUNCTION')
        self._exec(drop_sql)
        # nothing fancy required here, the sql is a create statement
        self._exec(sql)

    def sync_stored_procedure(self, path):
        """Syncs a stored procedure."""
        schema_dot_obj, sql = self._parse_path(path)[:2]
        self.logger.debug('Syncing stored procedure: %s', schema_dot_obj)
        drop_sql = _if_drop(schema_dot_obj, object_type='PROCEDURE')
        self._exec(drop_sql)
        # nothing fancy required here, the sql is a create statement
        self._exec(sql)

    def sync_job(self, path):
        """
        Takes a dict that could be interpreted from json, yaml, or python
        and creates a job, steps and schedule based on it.
        """
        with open(path, 'rb') as stream:
            job = yaml.load(stream)
        job_name, build_sql = read_job(job)
        drop_sql = """DECLARE @job_id binary(16);
        SELECT @job_id = job_id FROM msdb.dbo.sysjobs WHERE name = '%s'
        IF (@job_id IS NOT NULL)
        BEGIN
            EXEC msdb.dbo.sp_delete_job @job_id
        END""" % job_name
        self._exec(drop_sql)
        self._exec(build_sql)

    def test(self):
        """Runs a simple test select statement."""
        self._exec('SELECT * FROM INFORMATION_SCHEMA.TABLES')

    def _schema_path(self, name):
        """
        Return the name with the default schema path dot separated.
        """
        return '.'.join([self.schema, name])

    def _exec(self, sql):
        """
        Executes some sql, with a little logging.
        """
        self.logger.debug('Executing sql:\n\n%s...\n\n' % sql[:280])
        self.cursor.execute(sql)
        try:
            rows = self.cursor.fetchall()
        except pymssql.OperationalError:
            self.logger.debug('0 rows')
        else:
            i = 0
            for i, row in enumerate(rows):
                self.logger.debug(row)
            self.logger.debug('%d rows' % i)
            return rows

def _if_drop(schema_dot_obj, object_type='VIEW'):
    """Generates sql to check for object and drop if it exists."""
    args = {
        'schema_dot_obj': schema_dot_obj,
        'object_type': object_type
        }
    sql = """IF OBJECT_ID ('%(schema_dot_obj)s') IS NOT NULL
    DROP %(object_type)s %(schema_dot_obj)s;"""
    return sql % args

def read_job(job):
    """
    Parses a job object.
    """
    sql = 'USE msdb;\n\n'
    job_template = """EXEC sp_add_job
    @job_name = %s,
    @notify_level_email = 3,
    @notify_email_operator_name = N'Dan Cohen',
    @notify_level_eventlog = 0
    ;\n\n"""

    formatters = OrderedDict([
        ('steps', format_step),
        ('schedules', format_sched),
        ('alerts', format_alert),
    ])

    for job_name, settings in job.items():
        sql += job_template % job_name

        for label, method in formatters.items():
            try:
                for attrs in settings[label]:
                    attrs['job_name'] = job_name
                    sql += method(attrs)
            except KeyError:
                pass

        print(sql)
        return job_name, sql

def format_step(step):
    """Returns SQL formatted add step command."""
    sql = """EXEC sp_add_jobstep
    @job_name = N'%(job_name)s',
    @step_name = N'%(step_name)s',
    @subsystem = N'TSQL',
    @command = '%(command)s'\n\n"""
    return sql % step

def format_freq_interval(fq):
    """Try to format the interval, but not too hard."""
    try:
        return TSQL_FREQ_INTS[fq]
    except KeyError:
        return fq

def format_sched(schedule):
    """Format the schedule values all nice, and set any missing defaults."""
    validators = {
        'active_start_date': lambda x: parse(x).strftime('%Y%m%d'),
        'freq_type': lambda x: TSQL_FREQ_TYPES[x],
        'freq_interval': format_freq_interval
    }
    for key, func in validators.items():
        schedule[key] = func(schedule[key])

    defaults = {
        'name': 'daily',
        'freq_type': 4,
        'freq_interval': 0,
        'freq_recurrence_factor': 0,
        'active_start_date': datetime.now().strftime('%Y%m%d'),
        'active_start_time': '0700'
    }
    for key in defaults.keys():
        try:
            schedule[key]
        except KeyError:
            schedule[key] = defaults[key]
    return build_exec_wparams('sp_add_jobschedule', schedule)

def format_alert(alert):
    """Returns a SQL formatted create alert command."""
    return build_exec_wparams('sp_add_alert', alert)

def build_exec_wparams(executable, params):
    """Returns TSQL formatted command to add an alert."""
    sql = 'EXEC %s' % executable
    delim = '\n'
    for key, val in params.items():
        sql += delim + '\t@%s = %s' % (key, val)
        delim = ',\n'
    return sql
