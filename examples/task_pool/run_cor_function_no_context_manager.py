import sys
import asyncio
from pathlib import Path
p = Path(__file__).absolute()
root = p.parent.parent.parent.absolute()
print(root)
sys.path.append(str(root))
from aio_parallel_tools import AioFixedTaskPoolSimple

async def test(name):
    print(f"{name} start")
    for i in range(5):
        await asyncio.sleep(1)
    result = f"{name} done"
    print(result)
    return "ok:" + result


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


if __name__ == "__main__":
    asyncio.run(main())
