"""
Tests for sqlalchemy deployer
"""
# pylint: disable=missing-docstring, import-error, wildcard-import
# pylint: disable=attribute-defined-outside-init,unused-wildcard-import, no-init
# pylint: disable=no-self-use
from __future__ import print_function

from nose.tools import *

from .tests import TestDeployableSql
from deployable_sql.deployers.sqlalchemy import SqlAlchemyDeployer


class TestSqlAlchemyDeployer(TestDeployableSql):
    def setup(self):
        super(TestSqlAlchemyDeployer, self).setup()
        self.d = SqlAlchemyDeployer('sqlite://')

    def teardown(self):
        super(TestSqlAlchemyDeployer, self).teardown()

    def test_sqlalchemy_deployer(self):
        ok_(self.d)

    @nottest
    def test_test(self):
        rows = self.d.test()
        ok_(rows)
