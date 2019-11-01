import asyncio
import random


async def worker(q):
    while True:
        msg = await q.get()
        print(msg)
        await asyncio.sleep(1)


async def prod(q, a):
    while True:
        await q.put((random.randint(1, 9), a))
        await asyncio.sleep(0.1)


async def main():
    q = asyncio.PriorityQueue()
    workers = [asyncio.create_task(worker(q)) for _ in range(5)]
    prds = [asyncio.create_task(prod(q, i)) for i in range(2)]
    await asyncio.sleep(10)

if __name__ == "__main__":
    asyncio.run(main())