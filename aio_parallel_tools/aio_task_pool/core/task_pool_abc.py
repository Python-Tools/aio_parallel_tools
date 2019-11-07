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


class AioTaskPoolABC(abc.ABC):
    """Asynchronous Task Pool Abstract Base Class.

    this pool is used when you need to limit the max number of parallel tasks at one time.
    It's a derivative of `Producer Consumer model`.
    The pool instance will manage a number of consumer as worker.
    You can scale the worker's number as you wish with the `scale` interface.
    And you, as the Producer, can send your task with the `submit` interface.
    If you want to close submit interface, you can use `pause` interface.

    """

    @abc.abstractproperty
    def paused(self) -> bool:
        """Check if user can submit tasks.

        If the task pool can accept new tasks,the result is False; else it's True.

        Returns:
            bool: can submit or not.

        """
        return NotImplemented

    @abc.abstractproperty
    def size(self) -> int:
        """Pool's size.

        Returns:
            int: Pool's size

        """
        return NotImplemented

    @abc.abstractproperty
    def closed(self) -> bool:
        """Check if the pool is closed."""
        return NotImplemented

    @abc.abstractproperty
    def waiting_tasks_number(self) -> int:
        """Now number of the waiting tasks.

        Returns:
            int: The number of the waiting tasks.

        """
        return NotImplemented

    @abc.abstractproperty
    def max_tasks_number(self) -> int:
        """Maximum number of the waiting tasks.

        Returns:
            int: The maximum number of the waiting tasks.

        """
        return NotImplemented

    @abc.abstractmethod
    async def __aenter__(self) -> "AioTaskPool":
        """Asynchronous Context Interface.

        You can use `async with` syntax to manager the task pool.
        This will call `start` interface in the beginning.
        """
        await self.start()
        return self

    @abc.abstractmethod
    async def __aexit__(self, exc_type, exc, tb) -> None:
        """Asynchronous Context Interface.

        You can use `async with` syntax to manager the task pool.
        This will call `close` interface in the end.
        """
        await self.close()

    @abc.abstractmethod
    async def start(self) -> None:
        """Initialize workers and open the task pool to accept tasks."""
        return NotImplemented

    @abc.abstractmethod
    def pause(self) -> bool:
        """Pause the task pool.

        Returns:
            bool: Check if The task pool is paused

        """
        return NotImplemented

    @abc.abstractmethod
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
        return NotImplemented

    @abc.abstractmethod
    async def scale(self, num: int) -> int:
        """Scale the number of the task pool's worker.

        Args:
            num (int): num to scale.positive will increase the worker,negative will decrease the worker.

        Returns:
            int: the number will scale to.

        """
        return NotImplemented

    @abc.abstractmethod
    def scale_nowait(self, num: int, soft=True) -> int:
        """Scale the number of the task pool's worker without waiting.

        Args:
            num (int): num to scale.positive will increase the worker,negative will decrease the worker.
            soft (bool, optional): if True, this interface will send Signal to task pool to close workers;
             else number of random workers will be cancel. Defaults to True.

        Returns:
            int: the number will scale to.

        """
        return NotImplemented

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
        return NotImplemented

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
        return NotImplemented
