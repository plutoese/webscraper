import asyncio
import aiohttp
from libs.proxy.class_proxymanager import ProxyManager
import time
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor


class AsyncStaticScraper():
    def __init__(self, urls, using_proxy=False):
        self._urls = urls
        self._result = None
        self._using_proxy = using_proxy

    async def fetch_page(self, session, url, repeated=1000):
        try_time = 0
        try:
            with aiohttp.Timeout(10):
                if self._using_proxy:
                    proxy = ProxyManager().random_proxy
                    async with session.get(url, proxy=proxy) as response:
                        print('using proxy: {}'.format(proxy))
                        assert response.status == 200
                        return await response.read()
                else:
                    async with session.get(url) as response:
                        assert response.status == 200
                        return await response.read()

        except:
            try_time += 1
            if try_time <= repeated:
                return await self.fetch_page(session, url)
            else:
                print('Try to get too many times, but failed!')
                raise Exception

    def start(self):
        event_loop = asyncio.get_event_loop()
        with aiohttp.ClientSession(loop=event_loop) as session:
            tasks = [asyncio.ensure_future(self.fetch_page(session, url)) for url in self._urls]
            self._result = event_loop.run_until_complete(asyncio.gather(*tasks))

    @property
    def result(self):
        return self._result

if __name__ == '__main__':
    webs = ['http://www.163.com', 'http://www.sina.com.cn',
            'http://www.baidu.com', 'http://www.csdn.net',
            'http://www.dgtle.com/portal.php']
    start = time.time()
    scraper = AsyncStaticScraper(urls=webs)
    scraper.start()

    print('Total: {}'.format(time.time()-start))