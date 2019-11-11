"""Asynchronous Actor Abstract Base Class."""
import abc
import asyncio
from typing import Any, List, Optional


class ActorABC:
    """Asynchronous Actor Abstract Base Class."""

    @abc.abstractclassmethod
    def Start(cls, num: int, inbox_maxsize: int = 0, loop: Optional[asyncio.events.AbstractEventLoop] = None, rev_timeout: Optional[int] = None):
        """Create and start a number of actor.

        Args:
            num (int): The number of actor to create and start.
            inbox_maxsize (int, optional): inbox's Size. Defaults to 0.
            loop (Optional[asyncio.events.AbstractEventLoop], optional): Event loop which the actors running on. Defaults to None.
            rev_timeout ([int], optional): timeout for waiting for the recive function. Defaults to None.

        """
        return NotImplemented

    @abc.abstractclassmethod
    def Restart(cls, num: int):
        """Restart a number of not available actor.

        Args:
            num (int): The number of actor to restart.

        """
        return NotImplemented

    @abc.abstractclassmethod
    async def Close(cls, num: int):
        """Close a number of available actor.

        Args:
            num (int): Close a number of available actor.

        """
        return NotImplemented

    @abc.abstractclassmethod
    def Clean(cls):
        """Clean all not available actors."""
        return NotImplemented

    @abc.abstractclassmethod
    async def Send(cls, message: Any, timeout: int):
        """Send message to the most available actor.

        Args:
            message (Any): Message to send to the actor.
            timeout (int): Timeout of the sending action.

        """
        return NotImplemented

    @abc.abstractclassmethod
    async def SendRandom(cls, message: Any, timeout):
        """Send message to a random available actor.

        Args:
            message (Any): Message to send to the actor.
            timeout (int): Timeout of the sending action.

        """
        return NotImplemented

    @abc.abstractclassmethod
    async def Publish(cls, message: Any, timeout: int):
        """Send message to all available actor.

        Args:
            message (Any): Message to send to the actor.
            timeout (int): Timeout of the sending action.

        """
        return NotImplemented

    @abc.abstractclassmethod
    def FindById(cls, aid: str) -> Any:
        """Find a actor instance by id.

        Args:
            aid (str): actor id in str

        Returns:
            Any: a actor instance.

        """
        return NotImplemented

    @abc.abstractclassmethod
    async def SendById(cls, aid: str, message: Any, timeout: int):
        """Find a actor instance by id to send message.

        Args:
            aid (str): actor id in str
            message (Any): Message to send to the actor.
            timeout (int): Timeout of the sending action.

        """
        return NotImplemented

    @abc.abstractclassmethod
    def RunningScope(cls) -> List[Any]:
        """Get the running actor instance.

        Returns:
            List[Any]: List of the running actor instance.

        """
        return NotImplemented

    @abc.abstractclassmethod
    def NotRunningScope(cls) -> List[Any]:
        """Get the not running actor instance.

        Returns:
            List[Any]: List of the running actor instance.

        """
        return NotImplemented

    @abc.abstractclassmethod
    def PausedScope(cls) -> List[Any]:
        """Get the paused actor instance.

        Returns:
            List[Any]: List of the paused actor instance.

        """
        return NotImplemented

    @abc.abstractclassmethod
    def NotPausedScope(cls) -> List[Any]:
        """Get the not paused actor instance.

        Returns:
            List[Any]: List of the not paused actor instance.

        """
        return NotImplemented

    @abc.abstractclassmethod
    def AvailableScope(cls) -> List[Any]:
        """Get the available actor instance.

        Returns:
            List[Any]: List of the available actor instance.

        """
        return NotImplemented

    @abc.abstractclassmethod
    def NotAvailableScope(cls) -> List[Any]:
        """Get the not available actor instance.

        Returns:
            List[Any]: List of the not available actor instance.

        """
        return NotImplemented

    @abc.abstractclassmethod
    def BestToSendScope(cls, num: int = None) -> List[Any]:
        """Get a number of the best to send actor instance.

        Returns:
            List[Any]: A number of the best to send actor instance.

        """
        return NotImplemented

    @abc.abstractproperty
    def available(self) -> bool:
        """Check if the actor instance is available.

        Returns:
            bool: if the actor instance is available.

        """
        return NotImplemented

    @abc.abstractproperty
    def paused(self) -> bool:
        """Check if the actor instance is paused.

        Returns:
            bool: if the actor instance is paused.

        """
        return NotImplemented

    @abc.abstractproperty
    def aid(self) -> str:
        """Get the id of the actor instance.

        Returns:
            bool: The id of the actor instance.

        """
        return NotImplemented

    @abc.abstractproperty
    def loop(self) -> asyncio.events.AbstractEventLoop:
        """The event loop tasks running on.

        Returns:
            asyncio.events.AbstractEventLoop: The event loop tasks running on.
        """
        return NotImplemented

    @abc.abstractproperty
    def inbox_maxsize(self) -> int:
        """Max size of the actor instance's message box.

        Returns:
            int: The max size of the actor instance's message box.

        """
        return NotImplemented

    @abc.abstractproperty
    def inbox_size(self) -> int:
        """Size of the actor instance's message box.

        Returns:
            int: Size of the actor instance's message box.

        """
        return NotImplemented

    @abc.abstractproperty
    def running(self) -> bool:
        """Check if the actor instance is running.

        Returns:
            bool: If the actor instance is running..

        """
        return NotImplemented

    @abc.abstractproperty
    def task(self) -> asyncio.Task:
        """Task running inside the actor instance.

        Returns:
            asyncio.Task: The task running inside the actor instance.

        """
        return NotImplemented

    @abc.abstractmethod
    def start(self):
        """Start the actor instance."""
        return NotImplemented

    @abc.abstractmethod
    async def close(self, timeout: Optional[int] = None):
        """Close the actor instance.

        Args:
            timeout (Optional[int], optional): timeout of closing action. Defaults to None.

        """
        return NotImplemented

    @abc.abstractmethod
    async def receive(self, message):
        """Define in your subclass.

        Args:
            message (Any): Message to send to the actor.
        """
        return NotImplemented

    @abc.abstractmethod
    def send_nowait(self, message):
        """Send a message to the actor instance with no wait.

        Args:
            message (Any): Message to send to the actor.

        """
        return NotImplemented

    @abc.abstractmethod
    async def send(self, message, timeout=None):
        """Send a message to the actor instance.

        Args:
            message (Any): Message to send to the actor.
            timeout (int): Timeout of the sending action.

        """
        return NotImplemented
