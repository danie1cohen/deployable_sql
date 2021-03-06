"""
Deployer object for T-SQL/MS-SQL
"""
from collections import OrderedDict
from datetime import datetime

from dateutil.parser import parse
import pymssql
import yaml

from .base_deployer import BaseDeployer
from . import constants


class PyMSSQLDeployer(BaseDeployer):
    """
    Class used to deploy source controlled SQL files to datbase.
    """
    def __init__(self, usr, pwd, host, db, **kwargs):
        """
        Prepare to create an engine connection.
        """
        super(PyMSSQLDeployer, self).__init__(**kwargs)
        self.usr = usr
        self.pwd = pwd
        self.host = host
        self.db = db
        self.conn = None
        self.cursor = None

    def connect(self):
        """
        Create a connection.
        """
        self.conn = pymssql.connect(self.host, self.usr, self.pwd, self.db)
        self.conn.autocommit(True)
        self.cursor = self.conn.cursor()

    def _reset_db(self):
        """
        Run a use statement on the default db.
        """
        self._exec('USE %s;' % self.db)

    def sync_view(self, path):
        """
        Drops the view if it already exists, then and recreates it.
        """
        schema_dot_obj, sql = self._parse_path(path)[:2]
        self.logger.debug('Syncing view: %s', schema_dot_obj)
        drop_sql = _if_drop(schema_dot_obj)

        # remove any ORDER BY statements
        sql = '\n'.join([line for line in sql.split('\n')
                         if 'ORDER BY' not in line])
        build_sql = "CREATE VIEW %s AS \n%s;" % (schema_dot_obj, sql)
        self._reset_db()
        self._exec(drop_sql)
        self._exec(build_sql)
        #self._exec('SELECT TOP 1 * FROM %s' % schema_dot_obj)
        self.logger.info('Deployed view: %s', schema_dot_obj)

    def sync_function(self, path):
        """
        Syncs a function.
        """
        schema_dot_obj, sql = self._parse_path(path)[:2]
        self.logger.debug('Syncing function: %s', schema_dot_obj)
        drop_sql = _if_drop(schema_dot_obj, object_type='FUNCTION')
        self._reset_db()
        self._exec(drop_sql)
        # nothing fancy required here, the sql is a create statement
        self._exec(sql)
        self.logger.info('Deployed function: %s', schema_dot_obj)

    def sync_stored_procedure(self, path):
        """
        Syncs a stored procedure.
        """
        schema_dot_obj, sql = self._parse_path(path)[:2]
        self.logger.debug('Syncing stored procedure: %s', schema_dot_obj)
        drop_sql = _if_drop(schema_dot_obj, object_type='PROCEDURE')
        self._reset_db()
        self._exec(drop_sql)
        # nothing fancy required here, the sql is a create statement
        self._exec(sql)
        self.logger.info('Deployed sp: %s', schema_dot_obj)

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
        self.logger.info('Deployed job: %s', schema_dot_obj)

    def sync_permission(self, path):
        """Ignore."""
        self.logger.warning('Ignoring "%s". U do it!', path)

    def test(self):
        """
        Runs a simple test select statement.
        """
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
        self.logger.debug('Executing sql:\n\n%s...\n\n', sql[:280])
        if self.conn is None:
            self.connect()

        self.cursor.execute(sql)
        try:
            rows = self.cursor.fetchall()
        except pymssql.OperationalError:
            self.logger.debug('0 rows')
        else:
            i = 0
            for i, row in enumerate(rows):
                self.logger.debug(row)
            self.logger.debug('%d rows', i)
            return rows

def _if_drop(schema_dot_obj, object_type='VIEW'):
    """
    Generates sql to check for object and drop if it exists.
    """
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
        ('servers', format_server),
    ])

    # there should be only one job per file but it will arrive as a dict
    assert len(job) == 1

    for job_name, settings in job.items():
        sql += job_template % job_name

        if 'servers' not in settings.keys():
            settings['servers'] = [{'job_name': job_name}]

        for label, method in formatters.items():

            attribute_list = settings.get(label, [])

            for i, attrs in enumerate(attribute_list):
                defaults = {}

                # for all steps that are not last, the default success
                # action should be to proceed to the next step
                if label == 'steps':
                    total_steps = len(attribute_list)

                    defaults['on_fail_action'] = constants.job_step_actions.QUIT_WITH_FAILURE

                    if i + 1 == total_steps:
                        defaults['on_success_action'] = constants.job_step_actions.QUIT_WITH_SUCCESS
                    else:
                        defaults['on_success_action'] = constants.job_step_actions.GO_TO_NEXT_STEP

                    on_success_action = attrs.get('on_success_action')
                    if isinstance(on_success_action, str):
                        attrs['on_success_action'] = constants.JOB_STEP_ACTIONS[on_success_action]

                    on_fail_action = attrs.get('on_fail_action')
                    if isinstance(on_fail_action, str):
                        attrs['on_fail_action'] = constants.JOB_STEP_ACTIONS[on_fail_action]

                defaults.update(attrs)

                defaults['job_name'] = job_name
                sql += method(defaults)

        return job_name, sql

def format_step(step):
    """
    Returns SQL formatted add step command.
    """
    defaults = {
        'subsystem': "N'TSQL'",
    }
    return build_exec_wparams('sp_add_jobstep', step, defaults=defaults)

def format_freq_interval(fq):
    """
    Try to format the interval, but not too hard.
    """
    try:
        return constants.FREQUENCY_INTERVALS[fq]
    except KeyError:
        return fq

def format_sched(schedule):
    """
    Format the schedule values all nice, and set any missing defaults.
    """
    defaults = {
        'name': 'daily',
        'freq_type': 4,
        'freq_interval': 0,
        'freq_recurrence_factor': 0,
        'active_start_date': datetime.now().strftime('%Y%m%d'),
        'active_start_time': '0700'
    }
    validators = {
        'active_start_date': lambda x: parse(x).strftime('%Y%m%d'),
        'freq_type': lambda x: constants.FREQUENCY_TYPES[x],
        'freq_interval': format_freq_interval
    }
    return build_exec_wparams('sp_add_jobschedule',
                              schedule,
                              defaults=defaults,
                              validators=validators)

def format_alert(alert):
    """
    Returns a SQL formatted create alert command.
    """
    return build_exec_wparams('sp_add_alert', alert)

def format_server(server):
    """
    Returns TSQL formatted command to set up a server.
    """
    return build_exec_wparams('sp_add_jobserver', server)

def build_exec_wparams(executable, params, defaults=None, validators=None):
    """
    Returns TSQL formatted command to add an alert.
    """
    if defaults is None: defaults = {}
    if validators is None: validators = {}

    for req in defaults.keys():
        if req not in params.keys():
            params[req] = defaults[req]

    for key, func in validators.items():
        params[key] = func(params[key])

    sql = 'EXEC %s' % executable
    delim = '\n'
    for key, val in params.items():
        sql += delim + '\t@%s = %s' % (key, val)
        delim = ',\n'
    return sql + '\n\n'
