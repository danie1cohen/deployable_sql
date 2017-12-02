"""
Tests for base deployer module
"""
# pylint: disable=missing-docstring, import-error, wildcard-import
# pylint: disable=attribute-defined-outside-init,unused-wildcard-import, no-init
# pylint: disable=no-self-use
from __future__ import print_function
import os

from nose.tools import *

from .tests import TestDeployableSql
from deployable_sql.deployers.base import BaseDeployer
from deployable_sql.folders import run_setup


class TestBaseDeployer(TestDeployableSql):
    def setup(self):
        super(TestBaseDeployer, self).setup()
        self.d = BaseDeployer()

    def teardown(self):
        super(TestBaseDeployer, self).teardown()
        if os.path.exists('views/test.sql'):
            os.remove('views/test.sql')
        if os.path.exists('views'):
            os.rmdir('views')

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

    def test_detect_path_missing(self):
        result = self.d._detect_path('missing.sql')
        assert_is_none(result)

    def write_test_file(self):
        if not os.path.exists('views'):
            os.mkdir('views')
        filename = 'views/test.sql'
        with open(filename, 'w') as stream:
            stream.write('SELECT *\nFROM TABLE\nWHERE CONDITION\n;')
        fullpath = os.path.abspath(filename)
        return fullpath

    def test_parse_path(self):
        fullpath = self.write_test_file()
        results = self.d._parse_path(fullpath)
        ok_(results)

    @raises(NotImplementedError)
    def test_sync_folder(self):
        fullpath = self.write_test_file()
        self.d.sync_folder(os.path.dirname(fullpath))
