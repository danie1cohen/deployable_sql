"""
Class that interacts with the database.
"""
import os

import pymssql


class BaseDeployer(object):
    """Base class for SQL Deployers."""
    def __init__(self, schema="cu", logger=None):
        self.schema = schema
        self.logger = logger


class PyMSSQLDeployer(BaseDeployer):
    """Class used to deploy source controlled SQL files to datbase"""
    def __init__(self, usr, pwd, host, db, **kwargs):
        """Creates an engine connection."""
        super(PyMSSQLDeployer, self).__init__(**kwargs)
        self.conn = pymssql.connect(host, usr, pwd, db)
        self.conn.autocommit(True)
        self.cursor = self.conn.cursor()

    def sync_view(self, path):
        """Drops the view if it already exists, then and recreates it."""
        self.logger.debug(path)
        self.logger.debug(os.path.splitext(os.path.basename(path)))
        filename, _ = os.path.splitext(os.path.basename(path))
        self.logger.debug('Syncing view: %s' % filename)
        with open(path, 'r') as stream:
            sql = stream.read()
        drop_sql = self._if_drop_view(filename)
        build_sql = self._create_view(filename, sql)
        self._exec(drop_sql)
        self._exec(build_sql)

    def sync_views(self, folder):
        """
        Syncs all the views in a given folder (that wend with ext .sql).
        """
        for vw in os.listdir(folder):
            if not vw.endswith('.sql'):
                continue
            self.sync_view(os.path.join(folder, vw))

    def test(self):
        """Runs a simple test select statement."""
        self._exec('SELECT * FROM INFORMATION_SCHEMA.TABLES')

    def _schema_path(self, name):
        """
        Return the name with the default schema path dot separated.
        """
        return '.'.join([self.schema, name])

    def _exec(self, sql):
        """
        Executes some sql, with a little logging.
        """
        self.logger.debug('Executing sql:\n\n%s...\n\n' % sql[:140])
        self.cursor.execute(sql)
        try:
            rows = self.cursor.fetchall()
        except pymssql.OperationalError:
            self.logger.debug('0 rows')
        else:
            i = 0
            for i, row in enumerate(rows):
                self.logger.debug(row)
            self.logger.debug('%d rows' % i)
            return rows

    def _if_drop_view(self, view):
        """Generates sql to check for object and drop if it exists."""
        path = self._schema_path(view)
        sql = """IF OBJECT_ID ('%s') IS NOT NULL
        DROP VIEW %s;""" % (path, path)
        return sql

    def _create_view(self, name, sql):
        """Turns a sql select statement into a create view statement."""
        return "CREATE VIEW %s AS \n%s;" % (self._schema_path(name), sql)
