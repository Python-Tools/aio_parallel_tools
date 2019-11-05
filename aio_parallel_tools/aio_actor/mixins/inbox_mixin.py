import asyncio
import warnings
from aio_parallel_tools.aio_actor.exception_and_warning import ActorTimeoutWarning


class InboxMixin:
    def __init__(self, inbox_maxsize=0):
        self._inbox = asyncio.Queue(maxsize=inbox_maxsize, loop=self.loop)

    @property
    def inbox(self):
        return self._inbox

    @property
    def inbox_maxsize(self):
        return self.inbox.maxsize

    @property
    def inbox_size(self):
        return self.inbox.qsize()

    def send_nowait(self, msg):
        '''
        Send a message to the actor
        '''
        self.inbox.put_nowait(msg)

    async def send(self, msg, timeout=None):
        '''Send a message to the actor.'''
        if not timeout:
            await self.inbox.put(msg)
        else:
            try:
                await asyncio.wait_for(self.inbox.put(msg), timeout=timeout)
            except asyncio.TimeoutError:
                await self.handle_send_timeout(msg)
            except Exception as e:
                raise e

    async def throw_error(self, error, timeout=None):
        await self.send(error, timeout=timeout)

    def throw_error_nowait(self, error):
        self.send_nowait(error)

    async def handle_send_timeout(self, msg):
        warnings.warn(f"msg {msg} send timeout", ActorTimeoutWarning)
