"""Define Signal object to send to worker."""


class TaskPoolSignal(Exception):
    """Signal for worker."""

    pass


class WorkerCloseSignal(TaskPoolSignal):
    """Signal for close worker."""

    pass
