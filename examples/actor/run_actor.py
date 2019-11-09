import asyncio
try:
    from aio_parallel_tools import AioActor, ActorManager
except ModuleNotFoundError as e:
    import sys
    from pathlib import Path
    p = Path(__file__).absolute()
    root = p.parent.parent.parent.absolute()
    sys.path.append(str(root))
    from aio_parallel_tools import AioActor, ActorManager


class Pinger(AioActor):
    async def receive(self, message):
        print(message)
        try:
            await ActorManager.get_actor("Ponger").Send('ping')
        except Exception as e:
            print(f"receive run error {e}")
        finally:
            await asyncio.sleep(0.5)


class Ponger(AioActor):
    async def receive(self, message):
        print(message)
        try:
            await ActorManager.get_actor("Pinger").Send('pong')
        except Exception as e:
            print(f"receive run error {e}")
        finally:
            await asyncio.sleep(0.5)


async def main():
    actors = ActorManager.has_actor()
    for actor_name in actors:
        A = ActorManager.get_actor(actor_name)
        A.Start(num=3)
    await asyncio.sleep(1)
    for i in ActorManager.get_actor("Pinger").Members:
        print("****************")
        print(i.aid)
        print(i.available)
        print(i.running)
        print(i.paused)
        print("****************")

    await ActorManager.get_actor("Pinger").Send("start")
    await asyncio.sleep(10)

    for actor_name in actors:
        A = ActorManager.get_actor(actor_name)
        await A.Close(num=3)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(main())
    finally:
        # 不管是什么异常，最终都要close掉loop循环
        loop.close()
