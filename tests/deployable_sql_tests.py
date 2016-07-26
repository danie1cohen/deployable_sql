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


class TestDeployableSql(object):
    def setup(self):
        print('SETUP!')

    def teardown(self):
        print('TEAR DOWN!')
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
        _ = BaseDeployer()

    def test_pymssql_deployer(self):
        pass
