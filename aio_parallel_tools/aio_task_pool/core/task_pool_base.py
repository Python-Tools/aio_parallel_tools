"""Base Task Pool Class."""
import asyncio
import concurrent
from typing import Optional
from .task_pool_abc import AioTaskPoolAbc


class AioTaskPoolBase(AioTaskPoolAbc):
    """Base Task Pool Class."""

    def __init__(self, *,

                 loop: Optional[asyncio.events.AbstractEventLoop] = None,
                 executor: concurrent.futures.Executor = None) -> None:
        """Initialize task pool.

        Args:
            init_size (int, optional): [description]. Defaults to 3.
            loop (Optional[asyncio.events.AbstractEventLoop], optional): [description]. Defaults to None.
            executor (concurrent.futures.Executor, optional): [description]. Defaults to None.

        """
        self._loop = loop or asyncio.get_event_loop()

    @property
    def loop(self):
        """Event loop."""
        return self._loop

    async def __aenter__(self) -> AioTaskPoolAbc:
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

    async def start(self) -> None:
        """Initialize workers and open the task pool to accept tasks."""
        await self.start_workers()
        self.start_accept()
