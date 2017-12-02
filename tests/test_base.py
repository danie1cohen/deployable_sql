"""
Tests for base deployer module
"""
# pylint: disable=missing-docstring, import-error, wildcard-import
# pylint: disable=attribute-defined-outside-init,unused-wildcard-import, no-init
# pylint: disable=no-self-use
from __future__ import print_function

from nose.tools import *

from .tests import TestDeployableSql
from deployable_sql.deployers.base import BaseDeployer
from deployable_sql.folders import run_setup


class TestBaseDeployer(TestDeployableSql):
    def setup(self):
        super(TestBaseDeployer, self).setup()
        self.d = BaseDeployer()

    def test_base_deployer(self):
        assert self.d

    @raises(NotImplementedError)
    def test_sync_file_full(self):
        run_setup('blank', 'whatever', gitinit=False)
        self.d.sync_file('permissions/grant_deployable.sql')

    @raises(NotImplementedError)
    def test_sync_file_partial(self):
        run_setup('blank', 'whatever', gitinit=False)
        self.d.sync_file('grant_deployable.sql')

    #@raises(IllegalPathError)
    def test_sync_file_bad(self):
        # do not fail on bad files, just log
        self.d.sync_file('no_such_file.sql')
