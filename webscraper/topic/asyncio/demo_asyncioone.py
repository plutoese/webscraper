# coding = UTF-8

import aiohttp
import asyncio


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
            # we put the url in the dlq, so other consumers wil handle it
            await dlq.put(url)
            # lower the pace
            asyncio.sleep(5)
            # telling the queue we finished processing the massage
            main_queue.task_done()











