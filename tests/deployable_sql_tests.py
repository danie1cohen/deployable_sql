"""
Tests for deployable_sql module
"""
# pylint: disable=missing-docstring, import-error, wildcard-import
# pylint: disable=attribute-defined-outside-init,unused-wildcard-import, no-init
# pylint: disable=no-self-use
from __future__ import print_function
import os

from nose.tools import *


from deployable_sql.folders import run_setup, FOLDERS, FILES
from deployable_sql.db import BaseDeployer, PyMSSQLDeployer
from deployable_sql.exc import IllegalPathError


class TestDeployableSql(object):
    def setup(self):
        print('SETUP!')
        run_setup('blank', 'whatever', gitinit=False)
        self.b = BaseDeployer()

    def teardown(self):
        print('TEAR DOWN!')
        for f in FILES:
            if os.path.exists(f):
                os.remove(f)
        for f in FOLDERS:
            if os.path.exists(f):
                os.rmdir(f)

    def test_folders(self):
        for f in FOLDERS:
            assert os.path.exists(f)
        for f in FILES:
            assert os.path.exists(f)

    def test_base_deployer(self):
        assert self.b

    def test_pymssql_deployer(self):
        pass

    @raises(NotImplementedError)
    def test_sync_file_full(self):
        self.b.sync_file('permissions/grant_schema.sql')

    @raises(NotImplementedError)
    def test_sync_file_partial(self):
        self.b.sync_file('grant_schema.sql')

    @raises(IllegalPathError)
    def test_sync_file_bad(self):
        self.b.sync_file('no_such_file.sql')
