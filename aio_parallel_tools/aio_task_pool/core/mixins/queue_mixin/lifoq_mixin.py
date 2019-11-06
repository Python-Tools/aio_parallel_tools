"""Submit tasks and Send Signals using Lifo Q."""
import asyncio
from typing import Optional, Dict, List, Any, Callable, Union
from aio_parallel_tools.aio_task_pool.core.task import Task
from aio_parallel_tools.aio_task_pool.core.signal import WorkerCloseSignal


class LifoQMixin:
    """Submit tasks and Send Signals using Lifo Q.

    Requirement:

        loop (Property): Event loop.

    Support:

        queue(Property): Event loop.

        waiting_tasks_number(Property): Task size in queue.

        max_tasks_number(Property): Queue's max size.

        make_message (Method): Make task to message.

        make_close_signal (Method): Make worker colse signal.

        parser_message (Method): Parser messages from queue.
    """

    def __init__(self,
                 queue: Optional[asyncio.Queue] = None,
                 queue_maxsize: int = 0) -> None:
        """Initialize Simple Queue Mixin.

        Args:
            queue (Optional[asyncio.Queue], optional): using a exist queue. Defaults to None.
            queue_maxsize (int, optional): set the maxsize of a new queue. Defaults to 0.

        """
        if isinstance(queue, asyncio.LifoQueue):
            self._queue = queue
        else:
            self._queue = asyncio.LifoQueue(maxsize=queue_maxsize, loop=self.loop)

    @property
    def queue(self):
        """Queue for sending and receiving tasks."""
        return self._queue

    @property
    def waiting_tasks_number(self) -> int:
        """Now number of the waiting tasks.

        Returns:
            int: The number of the waiting tasks.

        """
        return self._queue.qsize()

    @property
    def max_tasks_number(self) -> int:
        """Maximum number of the waiting tasks.

        Returns:
            int: The maximum number of the waiting tasks.

        """
        return self._queue.maxsize

    def make_message(self, task: Task, **kwargs):
        """Make task message to send."""
        return task

    def make_close_signal(self):
        """Make close signal to send."""
        return WorkerCloseSignal

    def parser_message(self, message: Any) -> Any:
        """Parser messages from queue."""
        return message
