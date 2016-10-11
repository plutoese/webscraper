# coding=UTF-8

# --------------------------------------------------------------
# class_staticsitescraper文件
# @class: StaticSiteScraper类
# @introduction: StaticSiteScraper类用来进行静态网页数据抓取
# @dependency: requests，bs4及re包
# @author: plutoese
# @date: 2016.06.24
# --------------------------------------------------------------

from urllib.parse import urljoin
from bs4 import BeautifulSoup
from libs.class_mongodb import MongoDB
from libs.class_proxymanager import ProxyManager
import requests
import re


class StaticSiteScraper:
    """用来抓取网站数据

    :param str website: 网页地址
    :return: 无返回值
    """
    def __init__(self,website=None,label=None,proxy=None,pages=None):
        # 设置网站地址
        self.website = website

        # 设置数据库
        self.db = MongoDB()
        self.db.connect('cache','scraper')

        # 设置网页地址集合
        if pages is None:
            self.mongo_pages = set()
        else:
            self.mongo_pages = pages
        self.pages = set()

        # 设置标示
        self.label = label

        # 设置代理服务器
        if proxy is not None:
            print(proxy)
            self.proxies = {'http': ''.join(['http://',proxy])}
        else:
            self.proxies = None

    def get_current_page_content(self, beautifulsoup=True):
        """ 获得当前网页的内容

        :param bool beautifulsoup: 说明返回的内容是否是bs4对象
        :return: 返回网页内容
        :rtype: str或bs对象
        """
        try:
            if self.proxies is not None:
                print('Using Proxy......',self.proxies['http'])
                html = requests.get(url=self.website,timeout=30,proxies=self.proxies)
            else:
                html = requests.get(url=self.website,timeout=30)
        except requests.exceptions.RequestException as e:
            print('Download Error: ',e)
            return None
        if beautifulsoup:
            return BeautifulSoup(html.content, "lxml")
        else:
            return html.content

    def get_links(self,page_url,condition=None,cache=False):
        """ 获取链接网址

        :param str page_url: 相对网页路径
        :param str condition: 筛选条件
        :return: 无返回值
        """
        url = urljoin(self.website,page_url)
        print(url)
        try:
            html = requests.get(url=url,timeout=30).content
        except requests.exceptions.RequestException as e:
            print('Download Error: ',e)
            return None

        # 储存数据到MongoDB数据库
        if cache:
            if url not in self.mongo_pages:
                self.db.collection.insert_one({'web':url,
                                               'content':html,
                                               'label':self.label})

        bsobj = BeautifulSoup(html, "lxml")

        for link in bsobj.findAll("a", href=re.compile(condition)):
            if 'href' in link.attrs:
                if link.attrs['href'] not in self.pages:
                    # We have encountered a new page
                    newPage = link.attrs['href']
                    self.pages.add(newPage)
                    self.get_links(newPage,condition,cache=True)


if __name__ == '__main__':
    pmanager = ProxyManager()
    ramdomproxy = pmanager.recommended_proxies(number=1)[0]
    site_scraper = StaticSiteScraper('http://www.cuaa.net/cur/',proxy=ramdomproxy)
    print(site_scraper.get_current_page_content().title)
    site_scraper.get_links(page_url='',condition='(\.\./)|\#',cache=True)

