import asyncio
from typing import Optional, Dict, List, Any, Callable, Union
from aio_parallel_tools.aio_task_pool.exception import NotAvailable
from aio_parallel_tools.aio_task_pool.signal import WorkerCloseSignal


class LifoQMixin:
    """Submit tasks and Send Signals using Lifo Q.

    Requirement:
        _loop (Attributes): event loop.
        _make_task (Method): make_task before submit.
        paused (Property): check if task pool is paused

    Overload:
        waiting_tasks_number (Property): Now number of the waiting tasks.
        max_tasks_number (Property): Maximum number of the waiting tasks.
        submit (Asynchronous Method): Submit task to the task pool.
        submit_nowait (Method): Submit task to the task pool with no wait.
        close_worker (Asynchronous Method): Send a close signal to a worker.
        close_worker_nowait (Method): Send a close signal to a worker with no waiting.
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
            self._queue = asyncio.LifoQueue(maxsize=queue_maxsize, loop=self._loop)

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

    async def submit(self, task_func: Callable[[Any], Any], *,
                     args: List[Any] = [],
                     kwargs: Dict[str, Any] = {},
                     blocking: bool = True) -> Union[asyncio.Future, Any]:
        """Submit task to the task pool.

        Args:
            task_func (Callable[[Any], Any]): The task function which will be called by the workers.
            args (List[Any], optional): The positional parameters for the task function. Defaults to [].
            kwargs (Dict[str, Any], optional): The keyword parameters for the task function. Defaults to {}.
            blocking (bool, optional): set if waiting for the task's result. Defaults to True.

        Raises:
            NotAvailable: The task pool is paused

        Returns:
            Union[asyncio.Future, Any]: if blocking is True, submit will return the result of the task;
            else it will return a future which you can await it to get the result.

        """
        if not self.paused:
            task = self._make_task(task_func, args, kwargs)
            fut = task.fut
            if blocking:
                await self._queue.put(task)
                return await fut
            else:
                asyncio.create_task(self._queue.put(task))
                return fut
        else:
            raise NotAvailable("task pool is paused")

    def submit_nowait(self, task_func: Callable[[Any], Any], *,
                      args: List[Any] = [],
                      kwargs: Dict[str, Any] = {}) -> asyncio.Future:
        """Submit task to the task pool with no wait.

        Args:
            task_func (Callable[[Any], Any]): The task function which will be called by the workers.
            args (List[Any], optional): The positional parameters for the task function. Defaults to [].
            kwargs (Dict[str, Any], optional): The keyword parameters for the task function. Defaults to {}.

        Raises:
            NotAvailable: The task pool is paused or
            e: other exception
            NotAvailable: task pool is full, can not put task any more

        Returns:
            asyncio.Future: a future which you can await it to get the result.

        """
        if not self.paused:
            task = self._make_task(task_func, args, kwargs)
            fut = task.fut
            try:
                self._queue.put_nowait(task)
            except asyncio.QueueFull as qfe:
                raise NotAvailable("task pool can not put task any more")
            except Exception as e:
                raise e
            else:
                return fut
        else:
            raise NotAvailable("task pool is paused")

    async def close_worker(self) -> None:
        """Send a close signal to a worker."""
        await self._queue.put(WorkerCloseSignal)

    def close_worker_nowait(self) -> None:
        """Send a close signal to a worker with no waiting."""
        self._queue.put_nowait(WorkerCloseSignal)

    def parser_message(self, message)->Any:
        """Parser messages from queue."""
        return message