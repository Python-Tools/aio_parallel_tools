# Task Pool

We use task pool to limit the parallelism of asynchronous tasks.
Generally, asynchronous io tasks is easy to hit a bottleneck of server.
And connection pool usualy can only tell you that connection pool is full.
So we need a task pool to limit the parallelism of asynchronous tasks so that server's io limit will not so easy to reach.


## Kinds of task pool

Now there are 6 kinds of task pool:

+ worker number fixed task pool
  
  + `AioFixedTaskPoolSimple`
  + `AioFixedTaskPoolLifo`
  + `AioFixedTaskPoolPriority`


+ worker number auto scale task pool

  + `AioAutoScaleTaskPoolSimple`
  + `AioAutoScaleTaskPoolLifo`
  + `AioAutoScaleTaskPoolPriority`


## How to use

All of them can use as asynchronous context manager.

```python
async def test(name):
    print(f"{name} start")
    for i in range(5):
        await asyncio.sleep(1)
    result = f"{name} done"
    print(result)
    return "ok:"+ result
async def main():
    async with AioFixedTaskPoolSimple() as task_pool:
        print(f"test pool size {task_pool.size}")
        print("test 4 task with pool size 3")
        print("test await blocking submit")
        r = await task_pool.submit(test, func_args=["e"])
        assert r == "ok:e done"
        print("test await blocking submit")
        print("scale 3")
        await task_pool.scale(3)
        print(f"test pool size {task_pool.size}")
```

Task pools can also deal with a normal function, but it will be run in a `concurrent.futures.Executor`

```python
def test(name):
    print(f"{name} start")
    for i in range(5):
        time.sleep(1)
    result = f"{name} done"
    print(result)
    return "ok:" + result
async def main():
    executor = concurrent.futures.ProcessPoolExecutor()
    async with AioFixedTaskPoolSimple(executor=executor) as task_pool:
        async with AioFixedTaskPoolSimple() as task_pool:
        print(f"test pool size {task_pool.size}")
        print("test 4 task with pool size 3")
        await asyncio.gather(
            task_pool.submit(test, func_args=["c"]),
            task_pool.submit(test, func_args=["b"]),
            task_pool.submit(test, func_args=["a"]),
            task_pool.submit(test, func_args=["d"])
        )
```

Of course you can just use `start` and `close` to manage the task pool's Life Cycle.

```python
async def main():
    task_pool = AioFixedTaskPoolSimple()
    await task_pool.start()
    print(f"test pool size {task_pool.size}")
    print("test 4 task with pool size 3")
    print("test await blocking submit")
    r = await task_pool.submit(test, func_args=["e"])
    assert r == "ok:e done"
    print("test await blocking submit")
    print("scale 3")
    await task_pool.scale(3)
    print(f"test pool size {task_pool.size}")
    await task_pool.close()
```

## Operations

There are only 3 Operations:

+ `submit` Submit a task to the task pool.

    ```python
    result = await task_pool.submit(test, func_args=["e"])
    ```

    If you use a Priority task pool, you can submit with a int param `weight`, the more small the more fast to be execut.

    ```python
    result = await priority_task_pool.submit(test, func_args=["e"],weight=1)
    ```

+ `scale` Scale the worker's number to increase/decrease the parallelism.number must be a int,if it's negative,task pool will decrease the parallelism.

    ```python
    await task_pool.scale(-1)
    ```

+ `pause` Pause/unpause the task pool to manange if user can submit task.You can use `paused` to check if you can submit tasks.

    ```python
    await task_pool.pause()
    print(task_pool.paused)
    ```