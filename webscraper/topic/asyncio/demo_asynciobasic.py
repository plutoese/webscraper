import time
import asyncio
import aiohttp

NUMBERS = range(12)
URL = 'http://httpbin.org/get?a={}'

async def fetch_async(session, a):
    async with session.get(URL.format(a)) as r:
       data = await r.json()

    return data['args']['a']

start = time.time()
event_loop = asyncio.get_event_loop()
with aiohttp.ClientSession(loop=event_loop) as session:
    tasks = [asyncio.ensure_future(fetch_async(session,num)) for num in NUMBERS]
    results = event_loop.run_until_complete(asyncio.gather(*tasks))

for num, result in zip(NUMBERS, results):
   print('fetch({}) = {}'.format(num, result))

print('Use asyncio+requests+ThreadPoolExecutor cost: {}'.format(time.time() - start))