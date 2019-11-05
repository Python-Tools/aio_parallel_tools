import warnings
import uuid
import asyncio


class ActorExit(Exception):
    pass


class ActorTimeoutWarning(Warning):
    pass


class InboxNearllyFullWarning(Warning):
    pass


class Actor:

    def __init__(self, inbox_maxsize=0, loop=None, rev_timeout=None):
        self.id = str(uuid.uuid4())
        self.loop = loop or asyncio.get_event_loop()
        self.inbox_maxsize = inbox_maxsize
        self.inbox = asyncio.Queue(maxsize=inbox_maxsize, loop=self.loop)
        self.running = False
        self.rev_timeout = rev_timeout
        self.task = None

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
        if self.inbox_maxsize > 3 and self.inbox_maxsize > self.inbox.qsize() >= int(self.inbox_maxsize * 0.8):
            warnings.warn(f"inbox {self.id} nearly full", InboxNearllyFullWarning)
        return True

    def before_actor_start(self):
        """actor启动前执行的钩子."""
        pass

    def after_actor_start(self):
        """actor启动后执行的钩子."""
        pass

    def befor_actor_colse(self):
        """actor关闭前执行的钩子."""
        pass

    def after_actor_close(self, task):
        """actor关闭后执行的钩子."""
        pass

    async def before_deal_rev(self, msg):
        """每次处理收到的消息前执行的钩子."""
        return msg

    async def after_deal_rev(self, result):
        """每次处理收到的消息后执行的钩子."""
        pass

    async def before_every_loop(self):
        """每个循环执行前执行的钩子."""
        pass

    async def after_every_loop(self):
        """每个循环执行后执行的钩子."""
        pass

    def send_nowait(self, msg):
        '''
        Send a message to the actor
        '''
        self.inbox.put_nowait(msg)

    async def send(self, msg, timeout=None):
        '''
        Send a message to the actor
        '''
        if not timeout:
            await self.inbox.put(msg)
        else:
            try:
                await asyncio.wait_for(self.inbox.put(msg), timeout=timeout)
            except asyncio.TimeoutError:
                await self.handle_send_timeout()
            except Exception as e:
                raise e

    async def close(self, timeout=None):
        await self.send(ActorExit, timeout=timeout)

    def close_nowait(self):
        self.send_nowait(ActorExit)

    async def throw_error(self, error, timeout=None):
        await self.send(error, timeout=timeout)

    def throw_error_nowait(self, error):
        self.send_nowait(error)

    async def handle_send_timeout(self, msg):
        warnings.warn(f"msg {msg} send timeout", ActorTimeoutWarning)

    async def handle_rev_timeout(self):
        warnings.warn(f"actor {self.__class__.__name__} rev msg timeout", ActorTimeoutWarning)

    async def receive(self, message):
        """
        Define in your subclass.
        """
        raise NotImplemented()

    async def _run(self):
        await self.before_every_loop()
        self.running = True
        while self.running:
            await self.before_every_loop()
            try:
                if self.rev_timeout is None:
                    message = await self.inbox.get()
                else:
                    message = await asyncio.wait_for(self.inbox.get(), timeout=self.rev_timeout)
            except asyncio.TimeoutError:
                await self.handle_rev_timeout()
            else:
                message = await self.before_deal_rev(message)
                if message is ActorExit:
                    log.warn("actor closed")
                    self.running = False
                    self.befor_actor_colse()
                    asyncio.current_task().cancel()
                elif isinstance(message, Exception):
                    self.running = False
                    self.befor_actor_colse()
                    raise message
                else:
                    result = await self.receive(message)
                    await self.after_deal_rev(result)
            await self.after_every_loop()

    def start(self):
        self.before_actor_start()
        self.task = asyncio.create_task(self._run())
        self.task.add_done_callback(self.after_actor_close)
        self.after_actor_start()
