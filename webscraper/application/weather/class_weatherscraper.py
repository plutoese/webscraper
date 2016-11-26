# coding=UTF-8

# --------------------------------------------------------------
# class_weatherscraper文件
# @class: WeatherScraper类
# @introduction: WeatherScraper类用来抓取城市历史天气
# @datasource：http://lishi.tianqi.com/
# @dependency: requests，bs4及re包
# @author: plutoese
# @date: 2016.06.28
# --------------------------------------------------------------

import random
from bs4 import BeautifulSoup
from libs.class_mongodb import MongoDB
from libs.class_proxymanager import ProxyManager
from libs.class_multithread import MultiThread
from libs.class_staticsitescraper import StaticSiteScraper
from collections import OrderedDict
import re


class WeatherScraper:
    """ WeatherScraper类用来抓取城市历史天气

    :param str website: 网页地址
    :return: 无返回值
    """
    def __init__(self):
        # 初始化
        self.pmanager = ProxyManager()

        # 设置数据库
        self.db = MongoDB()
        self.db.connect('cache','scraper')

        # 地区
        self.set_region()

    def set_region(self):
        site_scraper = StaticSiteScraper('http://lishi.tianqi.com/',proxy=random.choice(self.pmanager.recommended_proxies(10)))
        html = site_scraper.get_current_page_content()

        # html parsing
        self.regions = OrderedDict()
        print(type(html))
        cities_link = html.select('#tool_site a')
        for link in cities_link:
            if re.search('http',str(link)) is not None:
                self.regions[re.sub('<|>','',re.findall('>.+<',str(link))[0])] =re.split('"',str(link))[1]

        print(len(self.regions))

    def parse_web_and_store(self,region):
        try:
            site_scraper = StaticSiteScraper(region,proxy=random.choice(self.pmanager.recommended_proxies(10)))
            html = site_scraper.get_current_page_content()
            for link in html.findAll("a", href=re.compile(''.join([re.sub('index\.html','',region),'\d+\.html']))):
                record = link.attrs['href']

                found = self.db.collection.find_one({'web':record})
                if found is None:
                    self.db.collection.insert_one({'web':record})
            return True
        except Exception as e:
            print('Parser Error: ',e)
            return False

    def one_thread(self,region):
        parse_done = False

        while not parse_done:
            parse_done = self.parse_web_and_store(region)

    def multi_thread(self, pool=None):
        """ 多线程验载入医院信息
        :return: 无返回值
        """
        threads = []
        for region in pool:
            t = MultiThread(self.one_thread,args=(region,),name=region)
            threads.append(t)

        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()

if __name__ == '__main__':
    wscraper = WeatherScraper()

    print(len(wscraper.regions))
    Max_number = 10
    pool = []
    for region in sorted(wscraper.regions):
        if len(pool) < Max_number:
            pool.append(wscraper.regions[region])
        else:
            wscraper.multi_thread(pool)
            pool = []

    if len(pool) > 0:
        print('Left: {}'.format(str(len(pool))))
        wscraper.multi_thread(pool)


