"""Define Exceptions of task pool."""


class TaskPoolException(Exception):
    """Task pool's exception."""

    pass


class UnknownTaskType(TaskPoolException):
    """Task type unknown Error."""

    pass


class UnknownTaskWeight(TaskPoolException):
    """Task weight unknown Error."""

    pass


class NotAvailable(TaskPoolException):
    """Task pool is not available."""

    pass


class TaskCancelled(TaskPoolException):
    """Error to raise when task was cancelled."""

    pass
