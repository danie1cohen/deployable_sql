"""
Class that interacts with the database.
"""
import os

import pymssql

from .exc import IllegalPathError


class BaseDeployer(object):
    """Base class for SQL Deployers."""
    def __init__(self, schema="cu", logger=None):
        self.schema = schema
        self.logger = logger

    def sync_function(self, path):
        """Syncs a function."""
        raise NotImplementedError

    def sync_permission(self, path):
        """Syncs a permission."""
        raise NotImplementedError

    def sync_stored_procedure(self, path):
        """Syncs an SP."""
        raise NotImplementedError

    def sync_table(self, path):
        """Syncs a table."""
        raise NotImplementedError

    def sync_view(self, path):
        """Syncs a view."""
        raise NotImplementedError

    def sync_file(self, path):
        """Syncs a file of not yet determined type."""
        path_mappings = {
            'functions': self.sync_function,
            'permissions': self.sync_permission,
            'stored_procedures': self.sync_stored_procedure,
            'tables': self.sync_table,
            'views': self.sync_view,

        }
        if os.path.sep in path:
            # if full path is provided, just decide on the right function
            segs = path.split(os.path.sep)
            if len(segs) != 2:
                raise IllegalPathError
            return path_mappings[segs[0]](path)
        else:
            # if partial path is provided, find the right folder
            for root, _, files in os.walk('.'):
                if '.git' in root:
                    continue
                for f in files:
                    if path == f:
                        clean_root = root.split(os.path.sep)[-1]
                        full_path = os.path.join(clean_root, f)
                        return path_mappings[clean_root](full_path)
        raise IllegalPathError


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

    def sync_table(self, path):
        """Not implemented."""
        raise NotImplementedError

    def sync_function(self, path):
        """Syncs a function."""
        raise NotImplementedError

    def sync_permission(self, path):
        """Syncs a permission."""
        raise NotImplementedError

    def sync_stored_procedure(self, path):
        """Syncs a stored procedure."""
        raise NotImplementedError

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
