"""Asynchronous Task Pool."""
import time
import copy
import random
import asyncio
import inspect
import concurrent
from collections import namedtuple
from typing import Optional, Dict, List, Any, Callable


Task = namedtuple(
    'Task',
    [
        'fut',
        'task_func',
        'args',
        'kwargs'
    ]
)


class UnknownTaskType(Exception):
    """Task type unknown Error."""

    pass


class TaskCancelled(Exception):
    """Error to raise when task was cancelled."""

    pass


class WorkerCloseSignal(Exception):
    """Signal for close worker."""

    pass


class AioTaskPool:
    """Asynchronous Task Pool Class.

    this pool is used when you need to limit the max number of parallel tasks at one time.
    It's a derivative of `Producer Consumer model`. 
    The pool instance will manage a number of consumer as worker.
    You can scale the worker's number as you wish with the `scale` interface.
    And you, as the Producer, can send your task with the `submit` interface.

    Attributes:
        init_size (int, optional): the size set when initial. Defaults to 3.
        loop (asyncio.events.AbstractEventLoop): the event loop which task pool running on.
        queue (asyncio.Queue): the queue which Distributing tasks.
        executor (concurrent.futures.Executor, optional): the executor used when the task function is normal function. Defaults to None.

    Property:
        size (int): 
        closed

    Example:
    >>> import asyncio
    >>> async def test(name):
    ...     print(f"{name} start")
    ...     for i in range(5):
    ...         await asyncio.sleep(1)
    ...     result = f"{name} done"
    ...     print(result)
    ...     return "ok:"+ result

    >>> async def main():
    ...     async with AioTaskPool() as task_pool:
    ...         print(f"test pool size {task_pool.size}")
    ...         print("test 4 task with pool size 3")
    ...         print("test await blocking submit")
    ...         r = await task_pool.submit(test, args=["e"])
    ...         assert r == "ok:e done"
    ...         print("test await blocking submit")
    ...         print("scale 3")
    ...         await task_pool.scale(3)
    ...         print(f"test pool size {task_pool.size}")
    ...
    ...         print("scale -3")
    ...         await task_pool.scale(-3)
    ...         print(f"test pool size {task_pool.size}")
    ...         await asyncio.sleep(2)
    ...         assert task_pool.size==6
    ...         print(f"after 2 s test pool size {task_pool.size}")

    """

    def __init__(self, *,
                 init_size: int = 3,
                 loop: Optional[asyncio.events.AbstractEventLoop] = None,
                 queue: Optional[asyncio.Queue] = None,
                 queue_maxsize: int = 0,
                 executor: concurrent.futures.Executor = None):
        """Initialize task pool.

        Args:
            init_size (int, optional): [description]. Defaults to 3.
            loop (Optional[asyncio.events.AbstractEventLoop], optional): [description]. Defaults to None.
            queue (Optional[asyncio.Queue], optional): [description]. Defaults to None.
            queue_maxsize (int, optional): [description]. Defaults to 0.
            executor (concurrent.futures.Executor, optional): [description]. Defaults to None.

        """
        self.init_size = init_size
        self.loop = loop or asyncio.get_event_loop()
        self.executor = executor
        self.queue = queue or asyncio.Queue(maxsize=queue_maxsize, loop=self.loop)
        self.workers = set()

    @property
    def size(self) -> int:
        """Pool's size.

        Returns:
            int: Pool's size

        """
        return len(self.workers)

    @property
    def closed(self) -> bool:
        """Check if the pool is closed."""
        return self.size == 0

    def start(self):
        """Initialize workers."""
        self._make_worker(self.init_size)

    def _make_task(self, task_func: Callable[[Any], Any],
                   args: List[Any] = [],
                   kwargs: Dict[str, Any] = {}):
        fut = self.loop.create_future()
        args = copy.deepcopy(args)
        kwargs = copy.deepcopy(kwargs)
        task = Task(fut, task_func, args, kwargs)
        return fut, task

    async def submit(self, task_func: Callable[[Any], Any], *,
                     args: List[Any] = [],
                     kwargs: Dict[str, Any] = {}, blocking=True):

        fut, task = self._make_task(task_func, args, kwargs)
        if blocking:
            await self.queue.put(task)
            return await fut
        else:
            asyncio.create_task(self.queue.put(task))
            return fut

    def submit_nowait(self, task_func: Callable[[Any], Any], *,
                      args: List[Any] = [],
                      kwargs: Dict[str, Any] = {}):
        fut, task = self._make_task(task_func, args, kwargs)
        self.queue.put_nowait(task)
        return fut

    async def close(self):
        for _ in range(self.size):
            await self.queue.put(WorkerCloseSignal)

    async def scale(self, num: int):
        if num > 0:
            self._make_worker(num)
        elif num < 0:
            num = abs(num)
            await self._remove_worker_soft(num)

    def close_nowait(self, soft=True):
        if soft:
            self._close_soft_nowait()
        else:
            self._close_hard()

    def scale_nowait(self, num: int, soft=True):
        if num > 0:
            self._make_worker(num)
        elif num < 0:
            num = abs(num)
            if soft:
                self._remove_worker_soft_nowait(num)
            else:
                self._remove_worker_hard(num)

    async def _task_handdler(self, fut, task_func, args, kwargs):
        if not inspect.isfunction(task_func):
            e = UnknownTaskType("task function must be coroutinefunction or normal function")
            raise e
        else:
            if inspect.isgeneratorfunction(task_func):
                e = UnknownTaskType("task function must be coroutinefunction or normal function")
                raise e
            elif inspect.iscoroutinefunction(task_func):
                return await task_func(*args, **kwargs)
            else:
                return await self.loop.run_in_executor(self.executor, task_func, *args, **kwargs)

    async def _worker(self):
        while True:
            message = await self.queue.get()
            if message is WorkerCloseSignal:
                break
            else:
                fut, task_func, args, kwargs = message
                try:
                    result = await self._task_handdler(fut, task_func, args, kwargs)
                except Exception as e:
                    fut.set_exception(e)
                else:
                    fut.set_result(result)
                finally:
                    self.queue.task_done()

    def _make_worker(self, number: int = 1):
        for _ in range(number):
            worker = asyncio.create_task(self._worker())
            worker.add_done_callback(lambda fut: self.workers.remove(fut))
            self.workers.add(worker)

    async def _remove_worker_soft(self, number: int = 1):
        for _ in range(number):
            await self.queue.put(WorkerCloseSignal)

    def _remove_worker_soft_nowait(self, number: int = 1):
        for _ in range(number):
            self.queue.put_nowait(WorkerCloseSignal)

    def _remove_worker_hard(self, number: int = 1):
        will_remove = random.choices(list(self.workers), k=number)
        for i in will_remove:
            i.cancel()

    def _close_soft_nowait(self):
        for _ in range(self.size):
            self.queue.put_nowait(WorkerCloseSignal)

    def _close_hard(self):
        for i in list(self.workers):
            i.cancel()

    async def __aenter__(self):
        self.start()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.close()
