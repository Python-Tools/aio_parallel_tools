"""Asynchronous Task Pool Class."""
import asyncio
import concurrent
from typing import Optional
from aio_parallel_tools.aio_task_pool.core.task_pool_base import AioTaskPoolBase
from aio_parallel_tools.aio_task_pool.core.mixins.queue_mixin.simpleq_mixin import SimpleQMixin
from aio_parallel_tools.aio_task_pool.core.mixins.worker_manager_mixin.fix_worker_manager_mixin import FixedWorkerManagerMixin
from aio_parallel_tools.aio_task_pool.core.mixins.producer_mixin.simple_producer_mixin import SimpleProducerMixin


class AioFixedTaskPoolSimple(SimpleProducerMixin, FixedWorkerManagerMixin, SimpleQMixin, AioTaskPoolBase):
    """Simple Asynchronous Task Pool Class.

    this pool is used when you need to limit the max number of parallel tasks at one time.
    It's a derivative of `Producer Consumer model`.
    The pool instance will manage a number of consumer as worker.
    You can scale the worker's number as you wish with the `scale` interface.
    And you, as the Producer, can send your task with the `submit` interface.
    If you want to close submit interface, you can use `pause` interface.

    Property:

        loop (asyncio.events.AbstractEventLoop):Event loop running on.

        size (int): The worker pool's size.

        closed (bool): Check if the worker pool's size is 0 and the worker pool is paused

        paused (bool): Check if the worker pool is paused. If can accept new tasks,the result is False; else it's True.

        waiting_tasks_number (int): The number of the waiting tasks.

        max_tasks_number (int): The maximum number of the waiting tasks.

    Method:

        pause (function): Pause the task pool.

        scale_nowait (function): Scale the number of the task pool's worker without waiting.

        submit_nowait (function): Submit task to the task pool with no wait.

    Asynchronous Method:

        start (function): Initialize workers and open the task pool to accept tasks.

        close (function): Close all workers and paused the task pool.

        scale (function): Scale the number of the task pool's worker.

        submit (function): Submit task to the task pool.

    Example:

    >>> import asyncio
    >>> async def test(name):
    ...     print(f"{name} start")
    ...     for i in range(5):
    ...         await asyncio.sleep(1)
    ...     result = f"{name} done"
    ...     print(result)
    ...     return "ok:"+ result
    >>> async def main():
    ...     async with AioFixedTaskPoolSimple() as task_pool:
    ...         print(f"test pool size {task_pool.size}")
    ...         print("test 4 task with pool size 3")
    ...         print("test await blocking submit")
    ...         r = await task_pool.submit(test, func_args=["e"])
    ...         assert r == "ok:e done"
    ...         print("test await blocking submit")
    ...         print("scale 3")
    ...         await task_pool.scale(3)
    ...         print(f"test pool size {task_pool.size}")
    ...
    ...         print("scale -3")
    ...         await task_pool.scale(-3)
    ...         print(f"test pool size {task_pool.size}")
    ...         await asyncio.sleep(2)
    ...         assert task_pool.size==6
    ...         print(f"after 2 s test pool size {task_pool.size}")

    """

    def __init__(self, *,
                 init_size: int = 3,
                 loop: Optional[asyncio.events.AbstractEventLoop] = None,
                 executor: concurrent.futures.Executor = None,
                 queue: Optional[asyncio.Queue] = None,
                 queue_maxsize: int = 0) -> None:
        """Initialize task pool.

        Args:
            init_size (int, optional): Set the binginning size of task pool. Defaults to 3.
            loop (Optional[asyncio.events.AbstractEventLoop], optional): Event loop running on.. Defaults to None.
            queue (Optional[asyncio.Queue], optional): Using a exist queue. Defaults to None.
            queue_maxsize (int, optional): Set the maxsize of a new queue. Defaults to 0.
            executor (concurrent.futures.Executor, optional): Executor to run synchronous functions. Defaults to None.

        """
        AioTaskPoolBase.__init__(self, loop=loop)
        SimpleQMixin.__init__(self, queue=queue, queue_maxsize=queue_maxsize)
        FixedWorkerManagerMixin.__init__(self, init_size=init_size, executor=executor)
        SimpleProducerMixin.__init__(self)
