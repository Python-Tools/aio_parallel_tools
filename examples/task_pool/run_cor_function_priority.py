import sys
import asyncio
from pathlib import Path
p = Path(__file__).absolute()
root = p.parent.parent.parent.absolute()
print(root)
sys.path.append(str(root))
from aio_parallel_tools import AioFixedTaskPoolPriority

async def test(name):
    print(f"{name} start")
    for i in range(5):
        await asyncio.sleep(1)
    result = f"{name} done"
    print(result)
    return "ok:" + result


async def main():
    async with AioFixedTaskPoolPriority() as task_pool:
        print(f"test pool size {task_pool.size}")
        print("test 4 task with pool size 3")
        await asyncio.gather(
            task_pool.submit(test, func_args=["c"],weight=5),
            task_pool.submit(test, func_args=["b"],weight=5),
            task_pool.submit(test, func_args=["a"],weight=5),
            task_pool.submit(test, func_args=["d"],weight=5)
        )
        print("test await blocking submit")
        r = await task_pool.submit(test, func_args=["e"], weight=5)
        print(r)
        print("test await no blocking submit")
        fut = await task_pool.submit(test, func_args=["f"], weight=5, blocking=False)
        r = await fut
        print(r)
        print("test await no blocking submit_nowait")
        fut = task_pool.submit_nowait(test, func_args=["h"], weight=5)
        r = await fut
        print(r)

        print("scale 3")
        await task_pool.scale(3)
        print(f"test pool size {task_pool.size}")

        print("scale -3")
        await task_pool.scale(-3)
        print(f"test pool size {task_pool.size}")
        await asyncio.sleep(2)
        print(f"after 2 s test pool size {task_pool.size}")

        print("scale_nowait 6")
        task_pool.scale_nowait(6)
        print(f"test pool size {task_pool.size}")

        print("scale_nowait -3 soft")
        task_pool.scale_nowait(-3)
        print(f"test pool size {task_pool.size}")
        await asyncio.sleep(2)
        print(f"after 2 s test pool size {task_pool.size}")

        print("scale_nowait -3 hard")
        task_pool.scale_nowait(-3, soft=False)
        print(f"test pool size {task_pool.size}")
        await asyncio.sleep(2)
        print(f"after 2 s test pool size {task_pool.size}")


if __name__ == "__main__":
    asyncio.run(main())
