"""
Base class for deployer objects.
"""
import logging
import os

from deployable_sql.exc import IllegalPathError


class BaseDeployer(object):
    """Base class for SQL Deployers."""
    def __init__(self, schema="cu"):
        self.schema = schema
        self.logger = logging.getLogger(__name__)

    def sync_function(self, path): # pragma: no cover
        """Syncs a function."""
        raise NotImplementedError

    def sync_permission(self, path): # pragma: no cover
        """Syncs a permission."""
        raise NotImplementedError

    def sync_stored_procedure(self, path): # pragma: no cover
        """Syncs an SP."""
        raise NotImplementedError

    def sync_table(self, path): # pragma: no cover
        """Syncs a table."""
        raise NotImplementedError

    def sync_view(self, path): # pragma: no cover
        """Syncs a view."""
        raise NotImplementedError

    def sync_job(self, path): # pragma: no cover
        """Syncs a job, step, schedule."""
        raise NotImplementedError

    def sync_file(self, name_or_path):
        """
        Syncs a file of not yet determined type.
        """
        path_mappings = {
            'functions': self.sync_function,
            'permissions': self.sync_permission,
            'stored_procedures': self.sync_stored_procedure,
            'sps': self.sync_stored_procedure,
            'tables': self.sync_table,
            'views': self.sync_view,
            'jobs': self.sync_job,
        }
        dirname, path = self._detect_path(name_or_path)
        return path_mappings[dirname](path)

    def _schema_path(self, name):
        """
        Return the name with the default schema path dot separated.
        """
        return name

    def _detect_path(self, name_or_path):
        """
        Return the path for a given input, which may be a filename, a filename
        relative to the source directory, or a full path.
        """
        full_path = None

        if os.path.exists(name_or_path):
            # handle full path or relative path by setting to absolute path
            full_path = os.path.abspath(name_or_path)
        else:
            # if partial path is provided, find the right folder
            for root, _, files in os.walk('.'):
                if '.git' in root:
                    continue
                for f in files:
                    if name_or_path == f:
                        clean_root = root.split(os.path.sep)[-1]
                        full_path = os.path.join(clean_root, f)

        if not os.path.exists(full_path):
            self.logger.warning('Could not find path for "%s"', name_or_path)
        else:
            return os.path.dirname(full_path), full_path

    def _parse_path(self, path):
        """
        Breaks the path up into its important elements and returns them as a
        tuple:
        """
        self.logger.debug('path: %s', path)

        filename = os.path.basename(path)
        basename, ext = os.path.splitext(filename)
        folder = os.path.dirname(path)
        self.logger.debug('parts: (%s, %s, %s)', folder, basename, ext)

        schema_dot_obj = self._schema_path(basename)
        self.logger.debug('schema.obj: %s', schema_dot_obj)

        # read sql from file
        with open(path, 'r') as stream:
            sql = stream.read()

        self.logger.debug('read sql: %s', sql[:140].replace('\n', ''))
        return schema_dot_obj, sql, folder, filename, basename

    def sync_folder(self, folder):
        """
        Syncs all the views in a given folder (that wend with ext .sql).
        """
        self.logger.debug('Looking for files in: %s', folder)
        for sql in os.listdir(folder):
            self.sync_file(os.path.join(folder, sql))
