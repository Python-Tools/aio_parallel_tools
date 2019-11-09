"""Fixed Worker Manager Mixin."""
import inspect
import asyncio
import random
import concurrent
from typing import Any
from aio_parallel_tools.aio_task_pool.core.exception import UnknownTaskType
from aio_parallel_tools.aio_task_pool.core.signal import WorkerCloseSignal
from aio_parallel_tools.aio_task_pool.core.task import Task


class FixedWorkerManagerMixin:
    """Fixed Worker Manager Mixin.

    Requirement:
        loop (Property): event loop.

        queue (Property): message queue.

        make_close_signal (Method): Make close signal to send.

        parser_message (Method): Parser messages from queue.

    Support:
        size (Property): worker set's size.

        start_workers (Asynchronous Method): Initialize workers and open the task pool to accept tasks.

        scale  (Asynchronous Method): Scale the number of the task pool's worker.

        scale_nowait (Method): Scale the number of the task pool's worker without waiting.

        close_workers (Asynchronous Method): Send worker pool size's close signal to the queue.

        close_workers_nowait_soft (Method): Send worker pool size's close signal to the queue with no wait.
        
        close_workers_hard (Method): Cancel worker hardlly.
    """

    def __init__(self, init_size: int = 3, executor: concurrent.futures.Executor = None):
        """Initialize task Fixed Worker Manager Mixin.

        Args:
            init_size (int, optional): Set the binginning size of task pool. Defaults to 3.
            executor (concurrent.futures.Executor, optional): Executor to run synchronous functions. Defaults to None.

        """
        self._workers = set()
        self._init_size = init_size
        self._executor = executor

    @property
    def size(self) -> int:
        """Pool's size.

        Returns:
            int: Pool's size

        """
        return len(self._workers)

    async def start_workers(self) -> None:
        """Initialize workers and open the task pool to accept tasks."""
        size = self._init_size - self.size
        await self.scale(size)

    async def scale(self, num: int) -> int:
        """Scale the number of the task pool's worker.

        Args:
            num (int): num to scale.positive will increase the worker,negative will decrease the worker.

        Returns:
            int: the number will scale to.

        """
        result = self.size + num
        if result > 0:
            if num > 0:
                self._make_worker(num)
            elif num < 0:
                num = abs(num)
                await self._remove_worker(num)
        else:
            result = 0
            num = self.size
            await self._remove_worker(num)
        return result

    def scale_nowait(self, num: int, soft=True) -> int:
        """Scale the number of the task pool's worker without waiting.

        Args:
            num (int): num to scale.positive will increase the worker,negative will decrease the worker.
            soft (bool, optional): if True, this interface will send Signal to task pool to close workers;
             else number of random workers will be cancel. Defaults to True.

        Returns:
            int: the number will scale to.

        """
        result = self.size + num
        if result > 0:
            if num > 0:
                self._make_worker(num)
            elif num < 0:
                num = abs(num)
                if soft:
                    self._remove_worker_nowait_soft(num)
                else:
                    self._remove_worker_hard(num)
        else:
            result = 0
            num = self.size
            if soft:
                self._remove_worker_nowait_soft(num)
            else:
                self._remove_worker_hard(num)
        return result

    async def _task_handdler(self, task: Task) -> Any:
        if not inspect.isfunction(task.task_func):
            e = UnknownTaskType("task function must be coroutinefunction or normal function")
            raise e
        else:
            if inspect.isgeneratorfunction(task.task_func):
                e = UnknownTaskType("task function must be coroutinefunction or normal function")
                raise e
            elif inspect.iscoroutinefunction(task.task_func):
                return await task.task_func(*task.args, **task.kwargs)
            else:
                return await self._loop.run_in_executor(self._executor, task.task_func, *task.args, **task.kwargs)

    async def _worker(self) -> None:
        while True:
            message = await self.queue.get()
            try:
                message = self.parser_message(message)
                if message is WorkerCloseSignal:
                    break
                else:
                    task = message
                    fut = task.fut
                    try:
                        result = await self._task_handdler(task)
                    except Exception as e:
                        fut.set_exception(e)
                    else:
                        fut.set_result(result)
            finally:
                self.queue.task_done()

    def _make_worker(self, number: int = 1) -> None:
        for _ in range(number):
            worker = asyncio.create_task(self._worker())
            worker.add_done_callback(lambda fut: self._workers.remove(fut))
            self._workers.add(worker)

    async def _remove_worker(self, number: int = 1) -> None:
        for _ in range(number):
            await self._close_worker()

    def _remove_worker_nowait_soft(self, number: int = 1) -> None:
        for _ in range(number):
            self._close_worker_nowait()

    def _remove_worker_hard(self, number: int = 1) -> None:
        will_remove = random.choices(list(self._workers), k=number)
        for i in will_remove:
            i.cancel()

    async def _close_worker(self) -> None:
        """Send a close signal to a worker."""
        message = self.make_close_signal()
        await self.queue.put(message)

    def _close_worker_nowait(self) -> None:
        """Send a close signal to a worker with no waiting."""
        message = self.make_close_signal()
        self.queue.put_nowait(message)

    async def close_workers(self):
        """Send worker pool size's close signal to the queue."""
        await self._remove_worker(self.size)

    def close_workers_nowait_soft(self) -> None:
        """Send worker pool size's close signal to the queue with no wait."""
        self._remove_worker_soft_nowait(self.size)

    def close_workers_hard(self) -> None:
        """Cancel worker hardlly."""
        for i in list(self._workers):
            i.cancel()
