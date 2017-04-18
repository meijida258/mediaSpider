import asyncio, time

loop = asyncio.get_event_loop()
asyncio.set_event_loop(loop)
start_time = time.time()
async def compute(a, b):
    print("Computing {} + {}...".format(a, b))
    await asyncio.sleep(a+b)
    return a+b
task = []
for i, j in zip(range(3), range(3)):
    print(i, j)
    task.append(compute(i, j))
loop.run_until_complete(asyncio.gather(*task))
loop.close()
print(time.time() - start_time)