Welcome to aio parallel tools's documentation!
==============================================

* version: 0.0.1
* status: dev
* author: huangsizhe
* email: hsz1273327@gmail.com


Desc
--------------------------------

Tools for creating asynchronous scripts easily.

keywords: tools,asyncio


Feature
----------------------
* Task pool 
* Actor and Actor Manager


Example
^^^^^^^^^^^^^^^^^^^

.. code:: python

    async with AioFixedTaskPoolSimple() as task_pool:
        print(f"test pool size {task_pool.size}")
        print("test 4 task with pool size 3")
        await asyncio.gather(
            task_pool.submit(test, func_args=["c"]),
            task_pool.submit(test, func_args=["b"]),
            task_pool.submit(test, func_args=["a"]),
            task_pool.submit(test, func_args=["d"])
        )

    class Pinger(AioActor):
        async def receive(self, message):
            print(message)
            try:
                await ActorManager.get_actor("Ponger").Send('ping')
            except Exception as e:
                print(f"receive run error {e}")
            finally:
                await asyncio.sleep(0.5)


Install
--------------------------------
- ``python -m pip install aio_parallel_tools``



Document
-------------------

https://python-tools.github.io/aio_parallel_tools/

Change Log
------------------

version 0.0.1
^^^^^^^^^^^^^^^^^^^

* created this project