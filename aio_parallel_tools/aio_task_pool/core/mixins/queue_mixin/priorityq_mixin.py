"""Submit tasks and Send Signals using Priority Q."""
import asyncio
import dataclasses
from typing import Optional, Dict, List, Any, Callable, Union
from aio_parallel_tools.aio_task_pool.core.task import Task
from aio_parallel_tools.aio_task_pool.core.signal import WorkerCloseSignal


@dataclasses.dataclass(order=True)
class PriorityTask:
    """Priority Task Message."""

    weight: int = dataclasses.field()
    task: Any = dataclasses.field(compare=False)


class PriorityQMixin:
    """Submit tasks and Send Signals using Priority Q.

    Requirement:

        loop (Property): event loop.
        
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
        if isinstance(queue, asyncio.PriorityQueue):
            self._queue = queue
        else:
            self._queue = asyncio.PriorityQueue(maxsize=queue_maxsize, loop=self.loop)

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
        weight = kwargs.get("weight", 4)
        pt = PriorityTask(weight, task)
        return pt

    def make_close_signal(self):
        """Make close signal to send."""
        pt = PriorityTask(1, WorkerCloseSignal)
        return pt

    def parser_message(self, message: PriorityTask) -> Any:
        """Parser messages from queue."""
        return message.task
