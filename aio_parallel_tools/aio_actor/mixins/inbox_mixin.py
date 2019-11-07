import asyncio
import warnings
from aio_parallel_tools.aio_actor.exception_and_warning import ActorTimeoutWarning, ActorIsPaused
from aio_parallel_tools.aio_actor.signal import ActorExit


class InboxMixin:
    def __init__(self, inbox_maxsize=0):
        self._inbox = asyncio.Queue(maxsize=inbox_maxsize, loop=self.loop)
        self._paused = True

    @property
    def inbox(self):
        """The Actor's message box."""
        return self._inbox

    @property
    def paused(self) -> bool:
        """Check if the Actor is paused."""
        return self._paused

    @property
    def inbox_maxsize(self) -> int:
        return self.inbox.maxsize

    @property
    def inbox_size(self) -> int:
        return self.inbox.qsize()

    def pause(self) -> bool:
        self._paused = not self._paused
        return self._paused

    def start_accept(self) -> None:
        self._paused = False

    def close_accept(self) -> None:
        """Close accept message."""
        self._paused = True

    def clean_inbox(self) -> List[Any]:
        """Clean the Actor's inbox.

        Raises:
            e: exception unknown

        Returns:
            List[Any]: the rest message not deal with.

        """
        self.close_accept()
        result = []
        while True:
            try:
                message = self.inbox.get_nowait()
            except asyncio.QueueEmpty as qee:
                break
            except Exception as e:
                raise e
            else:
                if message is not ActorExit and isinstance(message, Exception):
                    result.append(message)
                self.inbox.task_done()
        return result

    def send_nowait(self, msg) -> None:
        '''
        Send a message to the actor
        '''
        if self.paused:
            raise ActorIsPaused("choose another to send")
        self.inbox.put_nowait(msg)

    async def send(self, msg, timeout=None) -> None:
        '''Send a message to the actor.'''
        if self.paused:
            raise ActorIsPaused("choose another to send")
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
