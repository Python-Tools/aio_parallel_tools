import random
import asyncio
from typing import List, Any
from aio_parallel_tools.aio_actor.actor_abc import ActorABC
from aio_parallel_tools.aio_actor.exception_and_warning import NoAvailableActor


class ManageMixin:

    def __init__(self):
        self.__class__.Members.add(self)
        self.Members = None

    def remove(self):
        self.__class__.Members.remove(self)

    @classmethod
    def Start(cls: ActorABC, num: int, inbox_maxsize=0, loop=None, rev_timeout=None):
        instances = [cls(inbox_maxsize=inbox_maxsize, loop=loop, rev_timeout=rev_timeout) for _ in range(num)]
        [ins.start() for ins in instances]

    @classmethod
    def Restart(cls: ActorABC, num: int):
        candidates = cls.NotAvailableScope()
        if len(candidates) > num:
            candidates = random.choices(candidates, num)
        [ins.start() for ins in candidates]

    @classmethod
    async def Close(cls: ActorABC, num: int):
        candidates = list(cls.Members)
        if len(candidates) > num:
            candidates = random.choices(candidates, num)
        await asyncio.gather(*[ins.close() for ins in candidates])

    @classmethod
    def Clean(cls: ActorABC):
        """clean up all not running actors."""
        candidates = cls.NotRunningScope()
        result = []
        for ins in candidates:
            result.append(ins.clean_inbox())
            cls.Members.remove(ins)
            del ins
        return result

    @classmethod
    async def Send(cls: ActorABC, message: Any, timeout=None):
        candidates = cls.BestToSendScope()
        if len(candidates) > 0:
            ins = candidates[0]
            await ins.send(message, timeout)
        else:
            raise NoAvailableActor("No Available Actor.")

    @classmethod
    async def SendRandom(cls: ActorABC, message: Any, timeout=None):
        candidates = cls.AvailableScope()
        if len(candidates) > 0:
            ins = random.choice(candidates)
            await ins.send(message, timeout)
        else:
            raise NoAvailableActor("No Available Actor.")

    @classmethod
    async def Publish(cls: ActorABC, message: Any, timeout=None):
        candidates = cls.AvailableScope()
        await asyncio.gather(*[ins.send(message, timeout) for ins in candidates])

    @classmethod
    def FindById(cls: ActorABC, aid: str):
        candidates = list(cls.Members)
        return [i for i in candidates if i.aid == aid]

    @classmethod
    async def SendById(cls: ActorABC, aid: str, message: Any, timeout=None):
        candidates = cls.FindById(aid)
        if len(candidates) > 0:
            ins = [0]
            await ins.send(message, timeout)
        else:
            raise NoAvailableActor("No Available Actor.")

    @classmethod
    def RunningScope(cls: ActorABC) -> List[ActorABC]:
        return [i for i in list(cls.Members) if i.running is True]

    @classmethod
    def NotRunningScope(cls: ActorABC) -> List[ActorABC]:
        return [i for i in list(cls.Members) if i.running is False]

    @classmethod
    def PausedScope(cls: ActorABC) -> List[ActorABC]:
        return [i for i in list(cls.Members) if i.paused is True]

    @classmethod
    def NotPausedScope(cls: ActorABC) -> List[ActorABC]:
        return [i for i in list(cls.Members) if i.paused is False]

    @classmethod
    def AvailableScope(cls: ActorABC) -> List[ActorABC]:
        return [i for i in list(cls.Members) if i.available is True]

    @classmethod
    def NotAvailableScope(cls: ActorABC) -> List[ActorABC]:
        return [i for i in list(cls.Members) if i.available is False]

    @classmethod
    def BestToSendScope(cls: ActorABC, num: int = None) -> List[ActorABC]:
        candidates = cls.AvailableScope()
        result = sorted(candidates, key=lambda x: x.inbox_size)
        if num:
            result = result[:num]
        return result
