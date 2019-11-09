import abc
from typing import Any, List
from aio_parallel_tools.aio_actor.actor_manager import ActorManagerRegister

class ActorABC(metaclass=ActorManagerRegister):

    @abc.abstractclassmethod
    def Start(cls, num: int, inbox_maxsize=0, loop=None, rev_timeout=None):
        return NotImplemented

    @abc.abstractclassmethod
    def Restart(cls, num: int):
        return NotImplemented

    @abc.abstractclassmethod
    async def Close(cls, num: int):
        return NotImplemented

    @abc.abstractclassmethod
    def Clean(cls):
        return NotImplemented

    @abc.abstractclassmethod
    async def Send(cls, msg: Any, timeout):
        return NotImplemented

    @abc.abstractclassmethod
    async def SendRandom(cls, msg: Any, timeout):
        return NotImplemented

    @abc.abstractclassmethod
    async def Publish(cls, msg: Any, timeout: int):
        return NotImplemented

    @abc.abstractclassmethod
    def FindById(cls, aid: str):
        return NotImplemented

    @abc.abstractclassmethod
    async def SendById(cls, aid: str, msg: Any, timeout: int):
        return NotImplemented

    @abc.abstractclassmethod
    def RunningScope(cls) -> List[Any]:
        return NotImplemented

    @abc.abstractclassmethod
    def NotRunningScope(cls) -> List[Any]:
        return NotImplemented

    @abc.abstractclassmethod
    def PausedScope(cls) -> List[Any]:
        return NotImplemented

    @abc.abstractclassmethod
    def NotPausedScope(cls) -> List[Any]:
        return NotImplemented

    @abc.abstractclassmethod
    def AvailableScope(cls) -> List[Any]:
        return NotImplemented

    @abc.abstractclassmethod
    def NotAvailableScope(cls) -> List[Any]:
        return NotImplemented

    @abc.abstractclassmethod
    def BestToSendScope(cls, num: int = None) -> List[Any]:
        return NotImplemented

    @abc.abstractproperty
    def available(self):
        return NotImplemented

    @abc.abstractproperty
    def paused(self):
        return NotImplemented

    @abc.abstractproperty
    def id(self):
        return NotImplemented

    @abc.abstractproperty
    def loop(self):
        return NotImplemented

    @abc.abstractproperty
    def inbox_maxsize(self):
        return NotImplemented

    @abc.abstractproperty
    def inbox_size(self):
        return NotImplemented

    @abc.abstractproperty
    def running(self):
        return NotImplemented

    @abc.abstractproperty
    def task(self):
        return NotImplemented

    @abc.abstractmethod
    async def close(self, timeout=None):
        return NotImplemented

    @abc.abstractmethod
    async def receive(self, message):
        """
        Define in your subclass.
        """
        return NotImplemented

    @abc.abstractmethod
    def start(self):
        return NotImplemented

    @abc.abstractmethod
    def send_nowait(self, msg):
        '''
        Send a message to the actor
        '''
        return NotImplemented

    @abc.abstractmethod
    async def send(self, msg, timeout=None):
        '''
        Send a message to the actor.
        '''
        return NotImplemented
