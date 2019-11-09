"""The simplest mixin for creating and submiting tasks to task pool."""
import copy
import warnings
import asyncio
from typing import (Callable, Dict, Any, List, Union)
from aio_parallel_tools.aio_task_pool.core.exception import NotAvailable
from aio_parallel_tools.aio_task_pool.core.task import Task


class SimpleProducerMixin:
    """Simple Producer Mixin.

    Requirement: 

        queue (Property): message queue.

        loop (Property): event loop.

        size (Property): worker pool's size.

        waiting_tasks_number (Property): Waiting task size in queue.

        make_message (Method): make task to message


        close_workers (Asynchronous Method): Send worker pool size's close signal to the queue.

        close_workers_nowait_soft (Method): Send worker pool size's close signal to the queue with no wait.

        close_workers_hard (Method): Cancel worker hardlly.

    Support:

        paused (Property): Check if user can submit tasks.

        closed (Property): Check if the pool is closed.

        start_accept (Method): Start Accept tasks.

        pause (Method): Pause the task pool.

        submit (Asynchronous Method): Submit task to the task pool.

        submit_nowait (Method): Submit task to the task pool with no wait.

        close_pool (Asynchronous Method): Send close signal to all worker.

        close_pool_nowait (Method): Send close signal to all workers with no waiting.

    """

    def __init__(self):
        """Initialize Simple Producer Mixin."""
        self._paused = True

    @property
    def paused(self) -> bool:
        """Check if user can submit tasks.

        If the task pool can accept new tasks,the result is False; else it's True.

        Returns:
            bool: can submit or not.

        """
        return self._paused

    @property
    def closed(self) -> bool:
        """Check if the pool is closed."""
        return self.pause is True and self.size == 0

    def start_accept(self):
        """Start Accept tasks."""
        self._paused = False

    def pause(self) -> bool:
        """Pause the task pool.

        Returns:
            bool: Check if The task pool is paused

        """
        self._paused = not self._paused
        return self.paused

    def _make_task(self,
                   task_func: Callable[[Any], Any],
                   args: List[Any] = [],
                   kwargs: Dict[str, Any] = {}) -> Task:
        fut = self._loop.create_future()
        args = copy.deepcopy(args)
        kwargs = copy.deepcopy(kwargs)
        task = Task(fut, task_func, args, kwargs)
        return task

    async def submit(self,
                     task_func: Callable[[Any], Any], *,
                     func_args: List[Any] = [],
                     func_kwargs: Dict[str, Any] = {},
                     blocking: bool = True, **kwargs) -> Union[asyncio.Future, Any]:
        """Submit task to the task pool.

        Args:
            task_func (Callable[[Any], Any]): The task function which will be called by the workers.
            func_args (List[Any], optional): The positional parameters for the task function. Defaults to [].
            func_kwargs (Dict[str, Any], optional): The keyword parameters for the task function. Defaults to {}.
            blocking (bool, optional): Set if waiting for the task's result. Defaults to True.

        Raises:
            NotAvailable: The task pool is paused

        Returns:
            Union[asyncio.Future, Any]: if blocking is True, submit will return the result of the task;
            else it will return a future which you can await it to get the result.

        """
        if not self.paused:
            task = self._make_task(task_func, func_args, func_kwargs)
            fut = task.fut
            message = self.make_message(task, **kwargs)
            if blocking:
                await self.queue.put(message)
                return await fut
            else:
                asyncio.create_task(self.queue.put(message))
                return fut
        else:
            raise NotAvailable("task pool is paused")

    def submit_nowait(self,
                      task_func: Callable[[Any], Any], *,
                      func_args: List[Any] = [],
                      func_kwargs: Dict[str, Any] = {},
                      **kwargs) -> asyncio.Future:
        """Submit task to the task pool with no wait.

        Args:
            task_func (Callable[[Any], Any]): The task function which will be called by the workers.
            func_args (List[Any], optional): The positional parameters for the task function. Defaults to [].
            func_kwargs (Dict[str, Any], optional): The keyword parameters for the task function. Defaults to {}.

        Raises:
            NotAvailable: The task pool is paused or
            e: other exception
            NotAvailable: task pool is full, can not put task any more

        Returns:
            asyncio.Future: a future which you can await it to get the result.

        """
        if not self.paused:
            task = self._make_task(task_func, func_args, func_kwargs)
            fut = task.fut
            message = self.make_message(task, **kwargs)
            try:
                self.queue.put_nowait(message)
            except asyncio.QueueFull as qfe:
                raise NotAvailable("task pool can not put task any more")
            except Exception as e:
                raise e
            else:
                return fut
        else:
            raise NotAvailable("task pool is paused")

    async def _waiting_all_task_done(self):
        while self.waiting_tasks_number > 0:
            await asyncio.sleep(0.1)

    async def close_pool(self,
                         close_worker_timeout: Union[int, float, None] = None,
                         close_pool_timeout: int = 3,
                         safe: bool = True) -> None:
        """Close all workers and paused the task pool.

        Args:
            close_worker_timeout (Union[int, float, None], optional): Timeout for closing all workers. Defaults to None.
            close_pool_timeout (int, optional): Timeout for join left tasks. Defaults to 3.
            safe (bool, optional): when getting  exceptions, raise it or warning it. Defaults to True.

        Raises:
            te: close workers timeout.
            e: unknown error when closing workers.
            te: waiting for left tasks done timeout
            e: unknown error when waiting for left tasks done

        """
        self._paused = True
        if close_worker_timeout and isinstance(close_worker_timeout, (int, float)):
            await asyncio.wait_for(self._waiting_all_task_done(), timeout=close_worker_timeout)
        else:
            await self._waiting_all_task_done()
        try:
            await self.close_workers()
        except asyncio.TimeoutError as te:
            if safe:
                warnings.warn("close workers timeout")
            else:
                raise te
        except Exception as e:
            if safe:
                warnings.warn(f"unknown error {e} when closing workers")
            else:
                raise e
        finally:
            try:
                await asyncio.wait_for(self.queue.join(), timeout=close_pool_timeout)
            except asyncio.TimeoutError as te:
                if safe:
                    warnings.warn(f"waiting for left tasks done timeout, {self.waiting_tasks_number}")
                else:
                    raise te
            except Exception as e:
                if safe:
                    warnings.warn(f"unknown error {e} when waiting for left tasks done")
                else:
                    raise e

    def close_pool_nowait(self, soft: bool = True) -> None:
        """Close all workers and paused the task pool without waiting.

        Args:
            soft (bool, optional): if True, this interface will send Signal to task pool to close workers;
             else all workers will be cancel. Defaults to True.

        """
        self._paused = True
        if soft:
            self.close_workers_nowait_soft()
        else:
            self.close_workers_hard()
