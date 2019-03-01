"""
Tests for pymssql deployer module
"""
# pylint: disable=missing-docstring, import-error, wildcard-import
# pylint: disable=attribute-defined-outside-init,unused-wildcard-import, no-init
# pylint: disable=no-self-use
from __future__ import print_function

from nose.tools import *

from .tests import TestDeployableSql
from deployable_sql.deployers.pymssql_deployer import PyMSSQLDeployer, read_job


class TestPyMSSQLDeployer(TestDeployableSql):
    def setup(self):
        super(TestPyMSSQLDeployer, self).setup()
        self.d = PyMSSQLDeployer('user', 'pwd', 'host', 'db')
        self.job = {
            'testjob': {
                'steps': [
                    {
                        'database_name': 'master',
                        'command': "N'EXEC testjob;'",
                        'step_name': 'testjob'
                    }
                ],
                'schedules': [
                    {
                        'freq_recurrence_factor': 1,
                        'name': 'weekly',
                        'freq_interval': 'sunday',
                        'active_start_time': '060000',
                        'freq_type': 'weekly',
                        'active_start_date': '2019-03-01'
                    }
                ]
            }
        }


    def teardown(self):
        super(TestPyMSSQLDeployer, self).teardown()

    def test_read_job(self):
        print(self.job)
        job_name, sql = read_job(self.job)
        eq_(job_name, 'testjob')
        assert 'EXEC sp_add_job' in sql

    def test_read_job_multisched(self):
        second_sched = {
            'active_start_date': '2016-08-01',
            'active_start_time': '091000',
            'freq_type': 'once',
            'name': 'once',
            }
        self.job['testjob']['schedules'].append(second_sched)
        print('job', self.job)
        _, sql = read_job(self.job)
        eq_(sql.count('sp_add_jobschedule'), 2)
        print('sql', sql)
        assert '@on_failure_action = 2' in sql
