"""
Deployer that uses sqlalchemy connection strings
"""
from sqlalchemy import create_engine, text

from .base import BaseDeployer


class SqlAlchemyDeployer(BaseDeployer):
    """A deployer that uses sql alchemy conn strings."""
    def __init__(self, conn_string, **kwargs):
        super(SqlAlchemyDeployer, self).__init__(**kwargs)
        self.engine = create_engine(conn_string)

    def _exec(self, sql):
        """Execute a statement."""
        result = self.engine.execute(text(sql))
        rows = result.fetchall()
        self.logger.debug(rows)
        return rows

    def test(self):
        """Run a quick test to see if this even works."""
        self._exec('SELECT * FROM INFORMATION_SCHEMA')
