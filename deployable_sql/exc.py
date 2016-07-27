"""Exceptions for deployable SQL."""

class DeployableSQLError(Exception):
    """Base error class for this module."""
    pass

class IllegalPathError(DeployableSQLError):
    """To be raised when a file path is invalid."""
    pass
