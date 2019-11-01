"""Asynchronous Task Pool Base Class."""
import abc
import copy
import random
import asyncio
import inspect
import warnings
import concurrent
from typing import Optional, Dict, List, Any, Callable, Union, Tuple
from .task import Task
from .signal import WorkerCloseSignal
from .exception import UnknownTaskType


class AioTaskPoolBase(abc.ABC):
    """Asynchronous Task Pool Basic Class.

    this pool is used when you need to limit the max number of parallel tasks at one time.
    It's a derivative of `Producer Consumer model`.
    The pool instance will manage a number of consumer as worker.
    You can scale the worker's number as you wish with the `scale` interface.
    And you, as the Producer, can send your task with the `submit` interface.
    If you want to close submit interface, you can use `pause` interface.
    """

    def __init__(self, *,
                 init_size: int = 3,
                 loop: Optional[asyncio.events.AbstractEventLoop] = None,
                 executor: concurrent.futures.Executor = None) -> None:
        """Initialize task pool.

        Args:
            init_size (int, optional): [description]. Defaults to 3.
            loop (Optional[asyncio.events.AbstractEventLoop], optional): [description]. Defaults to None.
            executor (concurrent.futures.Executor, optional): [description]. Defaults to None.

        """
        self.init_size = init_size

        self._loop = loop or asyncio.get_event_loop()
        self._executor = executor
        self._workers = set()
        self._paused = True

    async def __aenter__(self) -> "AioTaskPool":
        """Asynchronous Context Interface.

        You can use `async with` syntax to manager the task pool.
        This will call `start` interface in the beginning.
        """
        await self.start()
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        """Asynchronous Context Interface.

        You can use `async with` syntax to manager the task pool.
        This will call `close` interface in the end.
        """
        await self.close()

    @property
    def paused(self) -> bool:
        """Check if user can submit tasks.

        If the task pool can accept new tasks,the result is False; else it's True.

        Returns:
            bool: can submit or not.

        """
        return self._paused

    @property
    def size(self) -> int:
        """Pool's size.

        Returns:
            int: Pool's size

        """
        return len(self._workers)

    @property
    def closed(self) -> bool:
        """Check if the pool is closed."""
        return self.pause is True and self.size == 0

    async def start(self) -> None:
        """Initialize workers and open the task pool to accept tasks."""
        size = self.init_size - self.size
        await self.scale(size)
        self._paused = False

    def pause(self) -> bool:
        """Pause the task pool.

        Returns:
            bool: Check if The task pool is paused

        """
        self._paused = not self._paused
        return self.paused

    async def close(self, close_worker_timeout: Union[int, float, None] = None, close_pool_timeout: int = 3, safe=True) -> None:
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
        try:
            if close_worker_timeout and isinstance(close_worker_timeout, (int, float)):
                await asyncio.wait_for(self._close_workers(), timeout=close_worker_timeout)
            else:
                await self._close_workers()
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
                await asyncio.wait_for(self._queue.join(), timeout=close_pool_timeout)
            except asyncio.TimeoutError as te:
                if safe:
                    warnings.warn("waiting for left tasks done timeout")
                else:
                    raise te
            except Exception as e:
                if safe:
                    warnings.warn(f"unknown error {e} when waiting for left tasks done")
                else:
                    raise e

    def close_nowait(self, soft=True) -> None:
        """Close all workers and paused the task pool without waiting.

        Args:
            soft (bool, optional): if True, this interface will send Signal to task pool to close workers;
             else all workers will be cancel. Defaults to True.

        """
        self._paused = True
        if soft:
            self._close_soft_nowait()
        else:
            self._close_hard()

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
                await self._remove_worker_soft(num)
        else:
            result = 0
            num = self.size
            await self._remove_worker_soft(num)
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
                    self._remove_worker_soft_nowait(num)
                else:
                    self._remove_worker_hard(num)
        else:
            result = 0
            num = self.size
            if soft:
                self._remove_worker_soft_nowait(num)
            else:
                self._remove_worker_hard(num)
        return result

    def _make_task(self,
                   task_func: Callable[[Any], Any],
                   args: List[Any] = [],
                   kwargs: Dict[str, Any] = {}) -> Task:
        fut = self._loop.create_future()
        args = copy.deepcopy(args)
        kwargs = copy.deepcopy(kwargs)
        task = Task(fut, task_func, args, kwargs)
        return task

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
            message = self.parser_message(await self._queue.get())
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
                    self._queue.task_done()

    def _make_worker(self, number: int = 1) -> None:
        for _ in range(number):
            worker = asyncio.create_task(self._worker())
            worker.add_done_callback(lambda fut: self._workers.remove(fut))
            self._workers.add(worker)

    async def _remove_worker_soft(self, number: int = 1) -> None:
        for _ in range(number):
            await self.close_worker()

    def _remove_worker_soft_nowait(self, number: int = 1) -> None:
        for _ in range(number):
            self.close_worker_nowait()

    def _remove_worker_hard(self, number: int = 1) -> None:
        will_remove = random.choices(list(self._workers), k=number)
        for i in will_remove:
            i.cancel()

    async def _close_workers(self):
        for _ in range(self.size):
            await self.close_worker()

    def _close_soft_nowait(self) -> None:
        for _ in range(self.size):
            self.close_worker_nowait()

    def _close_hard(self) -> None:
        for i in list(self._workers):
            i.cancel()

    @abc.abstractproperty
    def waiting_tasks_number(self) -> int:
        """Now number of the waiting tasks.

        Returns:
            int: The number of the waiting tasks.

        """
        raise NotImplemented

    @abc.abstractproperty
    def max_tasks_number(self) -> int:
        """Maximum number of the waiting tasks.

        Returns:
            int: The maximum number of the waiting tasks.

        """
        raise NotImplemented

    @abc.abstractmethod
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
        raise NotImplemented

    @abc.abstractmethod
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
        raise NotImplemented

    @abc.abstractmethod
    async def close_worker(self):
        """Send a close signal to a worker."""
        raise NotImplemented

    @abc.abstractmethod
    def close_worker_nowait(self):
        """Send a close signal to a worker with no waiting."""
        raise NotImplemented

    @abc.abstractmethod
    def parser_message(self,message):
        raise NotImplemented