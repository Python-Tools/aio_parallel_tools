"""Async Actor Tool."""
import warnings
import uuid
import asyncio

from aio_parallel_tools.aio_actor.mixins.hooks_mixin import HooksMixin
from aio_parallel_tools.aio_actor.mixins.id_mixin import IdentifyMixin
from aio_parallel_tools.aio_actor.mixins.inbox_mixin import InboxMixin
from aio_parallel_tools.aio_actor.mixins.task_mixin import TaskMixin
from aio_parallel_tools.aio_actor.mixins.loop_mixin import LoopMixin
from aio_parallel_tools.aio_actor.mixins.manage_mixin import ManageMixin

from aio_parallel_tools.aio_actor.actor_abc import ActorABC
from aio_parallel_tools.aio_actor.actor_manager import ActorManagerRegister
from aio_parallel_tools.aio_actor.exception_and_warning import InboxNearllyFullWarning
from aio_parallel_tools.aio_actor.signal import ActorExit


class AioActor(ManageMixin, InboxMixin, TaskMixin, HooksMixin, IdentifyMixin, LoopMixin, ActorABC, metaclass=ActorManagerRegister):
    """[summary]
    

    """

    def __init__(self, inbox_maxsize=0, loop=None, rev_timeout=None):
        ActorABC.__init__(self)
        LoopMixin.__init__(self, loop=loop)
        ManageMixin.__init__(self)
        IdentifyMixin.__init__(self)
        HooksMixin.__init__(self)
        TaskMixin.__init__(self, rev_timeout=rev_timeout)
        InboxMixin.__init__(self, inbox_maxsize=inbox_maxsize)

    @property
    def available(self):
        if self.task is None:
            return False
        if self.task.done():
            return False
        if self.running is False:
            return False
        if self.inbox.full():
            return False
        if self.paused:
            return False
        if self.inbox_maxsize > 3 and self.inbox_maxsize > self.inbox.qsize() >= int(self.inbox_maxsize * 0.8):
            warnings.warn(f"inbox {self.aid} nearly full", InboxNearllyFullWarning)
        return True

    async def close(self, timeout=None):
        await self.send(ActorExit, timeout=timeout)
        self.close_accept()
        await self.close_task()

    def close_nowait(self):
        self.send_nowait(ActorExit)

    def start(self):
        self.before_actor_start()
        self.start_accept()
        self.start_task()
        self.after_actor_start()
