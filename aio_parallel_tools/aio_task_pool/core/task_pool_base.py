"""Base Task Pool Class."""
import asyncio
import concurrent
from typing import Optional, Union, Any
from .task_pool_abc import AioTaskPoolABC


class AioTaskPoolBase(AioTaskPoolABC):
    """Base Task Pool Class."""

    def __init__(self, *, loop: Optional[asyncio.events.AbstractEventLoop] = None) -> None:
        """Initialize task pool.

        Args:
            loop (Optional[asyncio.events.AbstractEventLoop], optional): Event loop running on. Defaults to None.

        """
        self._loop = loop or asyncio.get_event_loop()

    @property
    def loop(self):
        """Event loop."""
        return self._loop

    async def __aenter__(self) -> AioTaskPoolABC:
        """Asynchronous Context Interface.

        You can use `async with` syntax to manager the task pool.
        This will call `start` interface in the beginning.
        """
        await self.start()
        return self

    async def __aexit__(self, exc_type: Any, exc: Any, tb: Any) -> None:
        """Asynchronous Context Interface.

        You can use `async with` syntax to manager the task pool.
        This will call `close` interface in the end.
        """
        await self.close()

    async def start(self) -> None:
        """Initialize workers and open the task pool to accept tasks."""
        await self.start_workers()
        self.start_accept()

    async def close(self,
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
        await self.close_pool(close_worker_timeout=close_worker_timeout, close_pool_timeout=close_pool_timeout, safe=safe)
