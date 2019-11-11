.. aio_parallel_tools documentation master file, created by
   sphinx-quickstart on Wed Oct 30 22:01:52 2019.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to aio parallel tools's documentation!
==============================================

Last change: |today|

Choose Locale:  :locale:`zh`  | :locale:`en`

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


Task pool
-------------------

.. toctree::
   :maxdepth: 2

   pages/task_pool
   pages/actor_and_manager


API
-------------------

.. toctree::
   :maxdepth: 4

   aio_parallel_tools


Change Log
------------------

version 0.0.1
^^^^^^^^^^^^^^^^^^^

* created this project