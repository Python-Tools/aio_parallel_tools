import asyncio
from typing import Optional, Dict, List, Any, Callable.Coroutine


class AioTaskPool:
    def __init__(self, *,
                 work_func: Callable[[Any], Coroutine[Any, Any, NoReturn]],
                 args: List[Any],
                 kwargs: Dict[str, Any],
                 min_size: int = 3,
                 max_size: int = 10,
                 loop: Optional[asyncio.events.AbstractEventLoop] = None,
                 queue: Optional[asyncio.Queue] = None,
                 queue_maxsize: int = 0):
        self.loop = loop or asyncio.get_event_loop()
        self.queue = queue or asyncio.Queue(maxsize=queue_maxsize, loop=self.loop)
        self.work_func = work_func
        self.args = args
        self.kwargs = kwargs
        self.min_size = min_size
        self.max_size = max_size
        self.workers = set()
        self._make_worker(self.min_size)

    @property
    def size(self):
        return len(self.workers)

    def keep_alive(self):
        for i in self.workers:
            if work

    def _worker(self):
        while True:


    def _make_worker(self, number: int = 1):
        for _ in range(number):
            worker = asyncio.create_task(self.work_func(*self.args, **self.kwargs))
            self.workers.add(worker)
