# coding=UTF-8

# --------------------------------------------------------------
# application_air_quality文件
# @introduction: 抓取空气质量的数据
# @source：天气后报，http://www.tianqihoubao.com/aqi/
# @dependency: requests，bs4及re包
# @author: plutoese
# @date: 2016.06.26
# --------------------------------------------------------------

import sys
from libs.class_mongodb import MongoDB
from libs.class_proxymanager import ProxyManager
from libs.class_staticsitescraper import StaticSiteScraper

# 1. 初始化参数
# 1.1 设置代理服务器
pmanager = ProxyManager()
ramdomproxy = pmanager.random_proxy

# 设置递归深度
sys.setrecursionlimit(1000000)

# 1.2 设置网页爬虫
db = MongoDB()
db.connect('cache','scraper')
pages = [item['webaddress'] for item in db.collection.find({'label':'airquality'},projection={'_id':0,'webaddress':1})]
site_scraper = StaticSiteScraper('http://www.tianqihoubao.com/aqi/',
                                 label='airquality',
                                 proxy=ramdomproxy,
                                 pages=set(pages))


# 2. 开始爬虫
site_scraper.get_links(page_url='',condition='/aqi/[a-zA-Z]+',cache=True)