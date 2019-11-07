import warnings
import asyncio
from aio_parallel_tools.aio_actor.exception_and_warning import ActorTimeoutWarning
from aio_parallel_tools.aio_actor.signal import ActorExit


class TaskMixin:

    def __init__(self, rev_timeout: int):
        self._rev_timeout = rev_timeout
        self._task = None
        self._running = False

    @property
    def running(self):
        return self._running

    @property
    def task(self):
        return self._task

    async def _run(self):
        await self.before_every_loop()
        self._running = True
        while self.running:
            await self.before_every_loop()
            try:
                if self.rev_timeout is None:
                    message = await self.inbox.get()
                else:
                    message = await asyncio.wait_for(self.inbox.get(), timeout=self._rev_timeout)
            except asyncio.TimeoutError:
                await self.handle_rev_timeout()
            else:
                try:
                    message = await self.before_deal_rev(message)
                    if message is ActorExit:
                        warnings.warn("actor closed")
                        self._running = False
                        self.befor_actor_colse()
                        asyncio.current_task().cancel()
                    elif isinstance(message, Exception):
                        self._running = False
                        self.befor_actor_colse()
                        raise message
                    else:
                        try:
                            result = await self.receive(message)
                        except Exception as e:
                            warnings.warn(f"actor {self.__class__.__name__} receive error: {e}")
                            try:
                                await self.after_deal_rev(message, e)
                            except Exception as e:
                                warnings.warn(f"actor {self.__class__.__name__} after deal rev error: {e}")
                        else:
                            try:
                                await self.after_deal_rev(message, result)
                            except Exception as e:
                                warnings.warn(f"actor {self.__class__.__name__} after deal rev error: {e}")
                finally:
                    self.inbox.task_done()
            finally:
                await self.after_every_loop()

    async def handle_rev_timeout(self):
        warnings.warn(f"actor {self.__class__.__name__} rev msg timeout", ActorTimeoutWarning)

    def start_task(self):
        if not self.running:
            task = asyncio.create_task(self._run())
            task.add_done_callback(self.after_actor_close)
            self._task = task
