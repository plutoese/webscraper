import asyncio
import json
import logging

import aiohttp
from aiohttp import ClientSession

# setting up logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
console = logging.StreamHandler()
logger.addHandler(console)
MAX_CONNECTION = 1000
URL_GET_POST = "https://hacker-news.firebaseio.com/v0/item/{}.json"
URL_MAX_ITEM = 'https://hacker-news.firebaseio.com/v0/maxitem.json'


# asyncio http consumer
async def consumer(main_queue, dlq, session, responses):
    while True:
        try:
            # Fetch the url from the queue, blocking until the queue has item
            url = await main_queue.get()
            # Try to get a response from the sever
            async with session.get(url, timeout=10) as response:
                # Check we got a valid response
                response.raise_for_status()
                # append it to the responses lists
                responses.append(await response.json())
                # telling the queue we finished processing the massage
                main_queue.task_done()
        # In case of a time in our get request/ problem with response code
        except (aiohttp.errors.HttpProcessingError, asyncio.TimeoutError) as e:
            logger.debug("Problem with %s, Moving to DLQ. main_queue: (%s), dlq: (%s)" %
                         (url, str(main_queue.qsize()), str(dlq.qsize())))
            # we put the url in the dlq, so other consumers wil handle it
            await dlq.put(url)
            # lower the pace
            asyncio.sleep(5)
            # telling the queue we finished processing the massage
            main_queue.task_done()


async def produce(queue, itr_items, base_url):
    for item in itr_items:
        # if the queue is full(reached maxsize) this line will be blocked
        # until a consumer will finish processing a url
        await queue.put(base_url.format(item))


async def download_last_n_posts(session, n, consumer_num):
    # We init the main_queue with a fixed size, and the dlq with unlimited size
    main_queue, dlq, responses = asyncio.Queue(maxsize=2000), asyncio.Queue(), []
    # we init the consumers, as the queues are empty at first,
    # they will be blocked on the main_queue.get()
    consumers = [asyncio.ensure_future(
        consumer(main_queue, dlq, session, responses))
                 for _ in range(consumer_num)]
    # init the dlq consumers, same as the base consumers,
    # Only main_queue is the dlq.
    dlq_consumers = [asyncio.ensure_future(
        consumer(main_queue=dlq, dlq=dlq, session=session, responses=responses))
                     for _ in range(10)]
    # get the max item from the API
    async with session.get(URL_MAX_ITEM) as resp:
        max_item = await resp.json()
    producer = await produce(queue=main_queue, itr_items=
    range(max_item, max_item - n, -1), base_url=URL_GET_POST)
    # wait for all item's inside the main_queue to get task_done
    await main_queue.join()
    # wait for all item's inside the dlq to get task_done
    await dlq.join()
    # cancel all coroutines
    for consumer_future in consumers + dlq_consumers:
        consumer_future.cancel()
    return responses


async def run(loop, n):
    conn_num = min(MAX_CONNECTION, n)
    # we init more connectors to get better performance
    with ClientSession(loop=loop, connector=aiohttp.TCPConnector(limit=conn_num)) as session:
        posts = await download_last_n_posts(session, n, conn_num)
        with open("hn_posts.json") as f:
            json.dump(posts)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run(loop, n=1000000))