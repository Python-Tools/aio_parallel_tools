import abc


class ActorABC(abc.ABC):

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
