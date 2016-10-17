# coding=UTF-8

# --------------------------------------------------------------
# class_hospitalscraper文件
# @class: HospitalScraper类
# @introduction: HospitalScraper类用来抓取医院信息
# @datasource：https://www.hqms.org.cn/usp/roster/index.jsp
# @dependency: requests，bs4及re包
# @author: plutoese
# @date: 2016.06.28
# --------------------------------------------------------------

import time
import random
from bs4 import BeautifulSoup
from libs.class_headlessbrowser import HeadlessBrowser
from libs.class_mongodb import MongoDB
from libs.class_proxymanager import ProxyManager
from selenium.webdriver.common.by import By
from libs.class_multithread import MultiThread
from libs.class_staticsitescraper import StaticSiteScraper
from libs.class_htmlparser import HtmlParser
import re


class AirQualityScraper:
    """ AirQualityScraper类用来抓取空气质量信息

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
        site_scraper = StaticSiteScraper('http://www.tianqihoubao.com/aqi/',proxy=random.choice(self.pmanager.best_speed_proxies))
        html = site_scraper.get_current_page_content()

        # html parsing
        self.regions = dict()
        htmlparser = HtmlParser(html_content=html)
        table = htmlparser.bs_obj.select('.citychk > dl')
        for item in table:
            row = item.find_all("a")
            for unit in row:
                three = re.split('\"',str(unit))
                self.regions[re.split('\s+<',re.split('>',three[2])[1])[0]] = re.split('\.',three[1])[0]

        print(len(self.regions))

    def one_thread(self,region):
        site_scraper = StaticSiteScraper('http://www.tianqihoubao.com/aqi/',proxy=random.choice(self.pmanager.best_speed_proxies))
        site_scraper.get_links(page_url=''.join([re.split('/aqi/',region)[1],'-201610.html']),
                                                condition=''.join(['^',region,'-.+']),cache=True)

    def multi_thread(self):
        """ 多线程验载入医院信息
        :return: 无返回值
        """
        '''
        while self.regions:
            region = self.regions[0]
            found = self.db.collection.find_one({'region':region,'label':'hospital'})
            if found is None:
                self.one_thread(region)
            else:
                self.regions.pop(0)'''

        threads = []
        for region in sorted(self.regions)[250:270]:
            t = MultiThread(self.one_thread,args=(self.regions[region],),name=region)
            threads.append(t)

        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()

if __name__ == '__main__':
    hscraper = AirQualityScraper()
    hscraper.multi_thread()

