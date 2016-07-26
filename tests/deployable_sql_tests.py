"""
Tests for deployable_sql module
"""
# pylint: disable=missing-docstring, import-error, wildcard-import
# pylint: disable=attribute-defined-outside-init,unused-wildcard-import, no-init
from __future__ import print_function
import os

from nose.tools import *

import deployable_sql


BASE_DIR = os.path.dirname(os.path.dirname(__file__))


class Testdeployable_sql(object):
    def setup(self):
        print('SETUP!')

    def teardown(self):
        print('TEAR DOWN!')

    def test_basic(self):
        print('I RAN!')
