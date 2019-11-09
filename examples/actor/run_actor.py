
import asyncio
import sys
import asyncio
from pathlib import Path
p = Path(__file__).absolute()
root = p.parent.parent.parent.absolute()
sys.path.append(str(root))
from aio_parallel_tools import AioActor

class Pinger(AioActor):
    async def receive(self, message):
        print(message)
        try:
            await Ponger.Send('ping')
        except Exception as e:
            print(f"receive run error {e}")
        finally:
            await asyncio.sleep(0.5)


class Ponger(AioActor):
    async def receive(self, message):
        print(message)
        try:
            await Pinger.Send('pong')
        except Exception as e:
            print(f"receive run error {e}")
        finally:
            await asyncio.sleep(0.5)


async def main():
    Pinger.Start(num=3)
    Ponger.Start(num=3)
    await asyncio.sleep(1)
    for i in Pinger.Members:
        print("****************")
        print(i.aid)
        print(i.available)
        print(i.running)
        print(i.paused)
        print("****************")

    await Pinger.Send("start")
    await asyncio.sleep(10)

    await Pinger.Close(num=3)
    await Ponger.Close(num=3)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(main())
    finally:
        # 不管是什么异常，最终都要close掉loop循环
        loop.close()
