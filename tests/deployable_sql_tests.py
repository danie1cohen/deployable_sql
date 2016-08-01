"""
Tests for deployable_sql module
"""
# pylint: disable=missing-docstring, import-error, wildcard-import
# pylint: disable=attribute-defined-outside-init,unused-wildcard-import, no-init
# pylint: disable=no-self-use
from __future__ import print_function
import os

from nose.tools import *


from deployable_sql.folders import run_setup, FOLDERS, FILES, create_job
from deployable_sql.db import (
    BaseDeployer, PyMSSQLDeployer, SqlAlchemyDeployer, read_job
    )
from deployable_sql.exc import IllegalPathError


BASE_DIR = os.path.dirname(os.path.dirname(__file__))

class TestDeployableSql(object):
    def setup(self):
        print('SETUP!')
        self.b = BaseDeployer()
        self.job = create_job('testjob')

    def teardown(self):
        print('TEAR DOWN!')
        if os.path.exists(os.path.join('jobs', 'testjob.yml')):
            os.remove(os.path.join('jobs', 'testjob.yml'))
        for f in FILES:
            if os.path.exists(f):
                os.remove(f)
        for f in FOLDERS:
            if os.path.exists(f):
                os.rmdir(f)

    def test_folders(self):
        run_setup('blank', 'whatever', gitinit=False)
        for f in FOLDERS:
            assert os.path.exists(f)
        for f in FILES:
            assert os.path.exists(f)

    def test_base_deployer(self):
        assert self.b

    def test_pymssql_deployer(self):
        #d = PyMSSQLDeployer('', '', '', '')
        pass

    def test_sqlalchemy_deployer(self):
        d = SqlAlchemyDeployer('sqlite://')
        ok_(d)

    @nottest
    def test_sqlalchemy_deployer(self):
        d = SqlAlchemyDeployer('mssql+pyodbc://svcDeployerSQL::qPU1NdiU0LFXIRgY6z5d@hosutons/ARCUSYM000')
        ok_(d.test())

    @raises(NotImplementedError)
    def test_sync_file_full(self):
        run_setup('blank', 'whatever', gitinit=False)
        self.b.sync_file('permissions/grant_deployable.sql')

    @raises(NotImplementedError)
    def test_sync_file_partial(self):
        run_setup('blank', 'whatever', gitinit=False)
        self.b.sync_file('grant_deployable.sql')

    @raises(IllegalPathError)
    def test_sync_file_bad(self):
        self.b.sync_file('no_such_file.sql')

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
        job_name, sql = read_job(self.job)
        eq_(sql.count('sp_add_jobschedule'), 2)
