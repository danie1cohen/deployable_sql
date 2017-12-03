"""
Tests for pymssql deployer module
"""
# pylint: disable=missing-docstring, import-error, wildcard-import
# pylint: disable=attribute-defined-outside-init,unused-wildcard-import, no-init
# pylint: disable=no-self-use
from __future__ import print_function

from nose.tools import *

from .tests import TestDeployableSql
from deployable_sql.deployers.pymssql import PyMSSQLDeployer, read_job


class TestPyMSSQLDeployer(TestDeployableSql):
    def setup(self):
        super(TestPyMSSQLDeployer, self).setup()
        #self.d = PyMSSQLDeployer('user', 'pwd', 'host', 'db')

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
        _, sql = read_job(self.job)
        eq_(sql.count('sp_add_jobschedule'), 2)
