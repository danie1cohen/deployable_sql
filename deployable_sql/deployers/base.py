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

    def sync_file(self, path):
        """Syncs a file of not yet determined type."""
        path_mappings = {
            'functions': self.sync_function,
            'permissions': self.sync_permission,
            'stored_procedures': self.sync_stored_procedure,
            'tables': self.sync_table,
            'views': self.sync_view,
            'jobs': self.sync_job,

        }
        if os.path.sep in path:
            if path.startswith('.' + os.path.sep):
                path = path.split(os.path.sep, 1)[-1]
            # if full path is provided, just decide on the right function
            segs = path.split(os.path.sep)
            if len(segs) != 2:
                self.logger.warning('%s', IllegalPathError(path))
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
        self.logger.warning('%s', IllegalPathError(path))

    def _parse_path(self, path):
        """
        Breaks the path up into its important elements and returns them as a
        tuple:
        """
        self.logger.debug('path: %s', path)

        folder = None
        if os.path.sep in path:
            segs = path.split(os.path.sep)
            if len(segs) != 2:
                self.logger.warning('%s', IllegalPathError(path))
            else:
                folder, filename = segs
        basename, ext = os.path.splitext(os.path.basename(path))
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
