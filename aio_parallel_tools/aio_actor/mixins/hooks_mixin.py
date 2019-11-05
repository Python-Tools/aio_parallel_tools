class HooksMixin:
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
