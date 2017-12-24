# coding=UTF-8

"""
=========================================
协程静态网页爬虫
=========================================

:Author: glen
:Date: 2017.12.17
:Tags: asyncio scraper
:abstract: 基于协程的静态网页爬虫

**类**
==================
AsyncStaticScraper
    基于协程的静态网页爬虫

**使用方法**
==================


**示范代码**
==================
::

"""

import asyncio
import aiohttp
from libs.proxy.class_proxymanager import ProxyManager
import time


class AsyncStaticScraper():
    def __init__(self, urls, request_type='get', response_type='text',using_proxy=False, processor=lambda x: x):
        self._urls = urls
        self._result = None
        self._request_type = request_type
        self._response_type = response_type
        self._using_proxy = using_proxy
        self._processor = processor

    async def fetch_page(self, session, url, repeated=1000):
        try_time = 0
        print('url: ',url)
        try:
            if self._using_proxy:
                proxy = ProxyManager().random_proxy
                print('Using Proxy: ',proxy)
                if isinstance(url, (tuple,list)):
                    if self._request_type == 'get':
                        scrape_fun = session.get(url[0], proxy=proxy, params=url[1])
                    else:
                        scrape_fun = session.post(url[0], data=url[1], proxy=proxy)
                else:
                    scrape_fun = session.get(url, proxy=proxy)
            else:
                if isinstance(url, (tuple, list)):
                    if self._request_type == 'get':
                        scrape_fun = session.get(url[0], params=url[1])
                    else:
                        scrape_fun = session.post(url[0], data=url[1])
                else:
                    scrape_fun = session.get(url)

            with aiohttp.Timeout(10):
                print('Iamhere...')
                async with scrape_fun as response:
                    assert response.status == 200
                    if self._response_type == 'json':
                        result = await response.json()
                    elif self._response_type == 'text':
                        result = await response.text()
                    else:
                        result = await response.read()
                    return self._processor(result), url
        except Exception as e:
            try_time += 1
            print('Try again!!...Meet exception {}'.format(e))
            if try_time <= repeated:
                return await self.fetch_page(session, url)
            else:
                print('Try to get too many times, but failed!')
                raise Exception

    def start(self):
        event_loop = asyncio.get_event_loop()
        with aiohttp.ClientSession(loop=event_loop,connector=aiohttp.TCPConnector(limit=20)) as session:
            tasks = [asyncio.ensure_future(self.fetch_page(session, url)) for url in self._urls]
            self._result = event_loop.run_until_complete(asyncio.gather(*tasks))

    @property
    def result(self):
        return self._result

if __name__ == '__main__':
    webs = ['http://www.163.com', 'http://www.sina.com.cn',
            'http://www.baidu.com', 'http://www.csdn.net',
            'http://www.dgtle.com/portal.php']
    #webs = ['https://randomuser.me/api/']*10
    start = time.time()
    scraper = AsyncStaticScraper(urls=webs)
    scraper.start()
    print(scraper.result)
    print('Total: {}'.format(time.time()-start))