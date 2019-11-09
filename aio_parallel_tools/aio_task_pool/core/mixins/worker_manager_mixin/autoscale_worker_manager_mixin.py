"""Fixed Worker Manager Mixin."""
import inspect
import asyncio
import warnings
import random
import concurrent
from collections import deque
import math
import statistics
from typing import Any, Optional
from aio_parallel_tools.aio_task_pool.core.exception import UnknownTaskType
from aio_parallel_tools.aio_task_pool.core.signal import WorkerCloseSignal
from aio_parallel_tools.aio_task_pool.core.task import Task


class AutoScaleWorkerManagerMixin:
    """Auto scale Worker Manager Mixin.

    Requirement:
        loop (Property): event loop.

        queue (Property): message queue.

        make_close_signal (Method): Make close signal to send.

        parser_message (Method): Parser messages from queue.

        waiting_tasks_number (Property): Now number of the waiting tasks.

        paused (Property): Check if user can submit tasks.


    Support:
        size (Property): worker set's size.

        start_workers (Asynchronous Method): Initialize workers and open the task pool to accept tasks.

        scale  (Asynchronous Method): Scale the number of the task pool's worker.

        scale_nowait (Method): Scale the number of the task pool's worker without waiting.

        close_workers (Asynchronous Method): Send worker pool size's close signal to the queue.

        close_workers_nowait_soft (Method): Send worker pool size's close signal to the queue with no wait.
        
        close_workers_hard (Method): Cancel worker hardlly.
        
        close_auto_scale_worker (Method): Close auto scale worker.
    """

    def __init__(self, *,
                 min_size: int = 3,
                 max_size: Optional[int] = None,
                 auto_scale_interval: int = 10,
                 auto_scale_cache_len: int = 20,
                 executor: concurrent.futures.Executor = None):
        """Initialize task Fixed Worker Manager Mixin.

        Args:
            min_size (int, optional): Min size of task pool. Defaults to 3.
            max_size (int, optional): Max size of task pool. Defaults to min_size+5.
            auto_scale_interval (int, optional): How often auto scale task run.
            executor (concurrent.futures.Executor, optional): executor to run synchronous functions. Defaults to None.

        """
        if not isinstance(min_size, int):
            raise AttributeError("min_size must be a int")
        if max_size is None:
            max_size = min_size + 5
        if not isinstance(max_size, int):
            raise AttributeError("max_size must be a int")
        if min_size >= max_size:
            raise AttributeError("max_size must bigger than min_size")
        self._workers = set()
        self._min_size = min_size
        self._max_size = max_size
        self._auto_scale_interval = auto_scale_interval
        self._auto_scale_cache_len = auto_scale_cache_len
        self._stat_cache = deque([], maxlen=self._auto_scale_cache_len)
        self._auto_scale_worker = None
        self._executor = executor

    @property
    def size(self) -> int:
        """Pool's size.

        Returns:
            int: Pool's size

        """
        return len(self._workers)

    def _auto_scale_worker_close_callback(self, fut):
        self._auto_scale_worker = None
        warnings.warn("auto_scale_worker closed")

    async def start_workers(self) -> None:
        """Initialize workers and open the task pool to accept tasks."""
        size = self._min_size - self.size
        await self.scale(size)
        if self._auto_scale_worker is None:
            self._auto_scale_worker = asyncio.create_task(self.start_auto_scale())
            self._auto_scale_worker.add_done_callback(self._auto_scale_worker_close_callback)
            warnings.warn("auto_scale_worker starting")

    def close_auto_scale_worker(self):
        """Close _auto_scale_worker."""
        self._auto_scale_worker.cancel()

    async def _auto_scale(self):
        if self.size == 0:
            if self.paused:
                return False
            else:
                await self.scale(self._min_size)
                return True
        score = self.waiting_tasks_number / self.size
        self._stat_cache.append(score)
        stat_cache = list(self._stat_cache)
        avg_score = statistics.mean(stat_cache)
        half_avg_score = statistics.mean(stat_cache[int(len(stat_cache) / 2):])
        quarter_avg_score = statistics.mean(stat_cache[int(len(stat_cache) * 3 / 4):])
        result = 0
        _range = self._max_size - self.size
        rate = 1
        if score > 2 and score > quarter_avg_score > half_avg_score > avg_score:
            warnings.warn("Task accumulation!")
            rate = 1
        if score > 2:
            rate = 0.6
        elif score >= 1:
            rate = 0.3
        elif score > 0 and score > quarter_avg_score:
            rate = 0.05
        else:
            _range = self._min_size - self.size
            rate = 0.1
            if quarter_avg_score < 0.1:
                rate += 0.2
                if half_avg_score < 0.1:
                    rate -= 0.2
                    if avg_score < 0.2:
                        rate -= 0.1
        if _range > 0:
            result = math.ceil(_range * rate)
        else:
            result = math.floor(_range * rate)
        await self.scale(result)
        return True

    async def start_auto_scale(self) -> None:
        while True:
            await asyncio.sleep(self._auto_scale_interval)
            await self._auto_scale()

    async def scale(self, num: int) -> int:
        """Scale the number of the task pool's worker.

        Args:
            num (int): num to scale.positive will increase the worker,negative will decrease the worker.

        Returns:
            int: the number will scale to.

        """
        result = self.size + num
        if result > self._max_size:
            result = self._max_size
            self._make_worker(self._max_size - self.size)
        elif self._max_size >= result >= self._min_size:
            if num > 0:
                self._make_worker(num)
            elif num < 0:
                num = abs(num)
                await self._remove_worker(num)
        else:
            result = self._min_size
            num = self.size - self._min_size
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
        if result > self._max_size:
            result = self._max_size
            self._make_worker(self._max_size - self.size)
        elif self._max_size >= result >= self._min_size:
            if num > 0:
                self._make_worker(num)
            elif num < 0:
                num = abs(num)
                if soft:
                    self._remove_worker_nowait_soft(num)
                else:
                    self._remove_worker_hard(num)
        else:
            result = self._min_size
            num = self.size - self._min_size
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
