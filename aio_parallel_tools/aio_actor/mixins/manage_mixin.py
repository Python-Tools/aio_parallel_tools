import random
import asyncio
from typing import List, Any
from aio_parallel_tools.aio_actor.actor_abc import ActorABC


class ManageMixin:

    def __init__(self):
        self.__class__.Members.add(self)
        self.Members = None

    def remove(self):
        self.__class__.Members.remove(self)

    @classmethod
    async def Start(cls: ActorABC, num: int, inbox_maxsize=0, loop=None, rev_timeout=None):
        instances = [cls(inbox_maxsize=inbox_maxsize, loop=loop, rev_timeout=rev_timeout) for _ in range(num)]
        await asyncio.gather(*[ins.start() for ins in instances])

    @classmethod
    async def Restart(cls: ActorABC, num: int):
        candidates = cls.NotAvailableScope()
        if len(candidates) > num:
            candidates = random.choices(candidates, num)
        await asyncio.gather(*[ins.start() for ins in candidates])

    @classmethod
    async def Close(cls: ActorABC, num: int):
        candidates = list(cls.Members)
        if len(candidates) > num:
            candidates = random.choices(candidates, num)
        await asyncio.gather(*[ins.close() for ins in candidates])

    @classmethod
    async def Clean(cls: ActorABC):
        """clean up all not running actors."""
        candidates = cls.NotRunningScope()
        for candidate in candidates:
            
        await asyncio.gather(*[ins.close() for ins in candidates])

    @classmethod
    def Send(cls: ActorABC, msg: Any):
        pass

    @classmethod
    def FindById(cls: ActorABC, id: Any):
        pass

    @classmethod
    async def Scale(cls: ActorABC, number: int):
        pass

    @classmethod
    async def Throw(cls: ActorABC, exception: Exception):
        pass

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
    def Best_To_Send_Scope(cls: ActorABC, num: int) -> List[ActorABC]:
        candidates = cls.AvailableScope()
        result = sorted(candidates, key=lambda x: x.inbox_size)[:num]
        return result
