"""
Tests for deployable_sql module
"""
# pylint: disable=missing-docstring, import-error, wildcard-import
# pylint: disable=attribute-defined-outside-init,unused-wildcard-import, no-init
# pylint: disable=no-self-use
from __future__ import print_function
import os

from nose.tools import *

from deployable_sql.folders import FOLDERS, FILES, create_job, run_setup
from deployable_sql.exc import *
from deployable_sql.central import *


class TestDeployableSql(object):
    def setup(self):
        print('SETUP!')
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
                for filename in os.listdir(f):
                    os.remove(os.path.join(f, filename))
                os.rmdir(f)

    def test_folders(self):
        run_setup('blank', 'whatever', gitinit=False)
        for f in FOLDERS:
            assert os.path.exists(f)
        for f in FILES:
            assert os.path.exists(f)
