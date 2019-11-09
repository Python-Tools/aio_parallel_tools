"""Define all hooks."""


class HooksMixin:
    """Define all hooks."""

    def before_actor_start(self):
        """Execute before actor start."""
        pass

    def after_actor_start(self):
        """Execute after actor start."""
        pass

    def befor_actor_colse(self):
        """Execute before actor close."""
        pass

    def after_actor_close(self, task):
        """Execute after actor close."""
        pass

    async def before_deal_rev(self, message):
        """每次处理收到的消息前执行的钩子."""
        return message

    async def after_deal_rev(self, message, result):
        """每次处理收到的消息后执行的钩子."""
        pass

    async def before_every_loop(self):
        """每个循环执行前执行的钩子."""
        pass

    async def after_every_loop(self):
        """每个循环执行后执行的钩子."""
        pass
